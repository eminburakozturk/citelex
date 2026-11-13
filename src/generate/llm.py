"""LLM istemcileri: Gemini (API), OpenRouter (API, model zinciri) ve Ollama (yerel). İkisi de generate(system, user) -> str.

temperature=0: aynı soru + aynı kaynaklar -> aynı cevap (eval tekrarlanabilirliği).
Ek bağımlılık yok; doğrudan HTTP (httpx). Gemini anahtarı başlıkta gider, URL'ye yazılmaz.
"""
from __future__ import annotations

import json
import os
import time
from collections.abc import Iterator

import httpx

from src import config


class LLMError(RuntimeError):
    def __init__(self, msg: str, status: int | None = None):
        super().__init__(msg)
        self.status = status   # sağlayıcının HTTP kodu (429 = kota); API bunu anlaşılır mesaja çevirir


def _retry_delay(r) -> float:
    """Gemini 429 gövdesindeki RetryInfo.retryDelay ("37s"); yoksa 0. En çok 70 sn."""
    if r.status_code != 429:
        return 0.0
    try:
        for d in r.json()["error"].get("details", []):
            if "retryDelay" in d:
                return min(float(str(d["retryDelay"]).rstrip("s")) + 1, 70.0)
    except (ValueError, KeyError, TypeError):
        pass
    return 30.0


class GeminiLLM:
    def __init__(self, model: str | None = None, timeout: float = 60):
        self.model = model or config.GEMINI_MODEL
        self.name = f"gemini:{self.model}"
        self._key = os.environ.get("GEMINI_API_KEY", "")
        if not self._key:
            raise LLMError("GEMINI_API_KEY yok (.env)")
        self._http = httpx.Client(timeout=timeout)

    def generate(self, system: str, user: str, max_tokens: int = 1500) -> str:
        r = None
        for attempt in range(4):  # 429/503/zaman aşımı geçici: 2, 6, 18 sn bekleyip yeniden dene
            try:
                r = self._post(system, user, max_tokens)
            except httpx.TimeoutException:
                if attempt == 3:
                    raise LLMError("Gemini zaman aşımı (4 deneme)") from None
                time.sleep(2 * 3 ** attempt)
                continue
            if r.status_code not in (429, 500, 503) or attempt == 3:
                break
            # 429'da sağlayıcının bildirdiği süre kadar beklenir (dakikalık kota: 2-18 sn'lik denemeler
            # yetmiyordu, eval 28. soruda durdu). Akışlı yol (API) beklemez; kullanıcıya mesaj döner.
            time.sleep(max(2 * 3 ** attempt, _retry_delay(r)))
        return self._parse(r)

    def _body(self, system: str, user: str, max_tokens: int) -> dict:
        return {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            # thinkingBudget=0: düşünme tokenları çıktı limitinden düşüp cevabı yarıda kesiyordu (ölçüldü: ~1100 token).
            "generationConfig": {"temperature": 0, "maxOutputTokens": max_tokens,
                                 "thinkingConfig": {"thinkingBudget": 0}},
        }

    def _post(self, system: str, user: str, max_tokens: int):
        return self._http.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
            headers={"x-goog-api-key": self._key}, json=self._body(system, user, max_tokens),
        )

    def stream(self, system: str, user: str, max_tokens: int = 1500) -> Iterator[str]:
        """Cevabı parça parça üretir (SSE). Geçici hatada yalnız İLK parça gelmeden önce yeniden denenir."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:streamGenerateContent"
        for attempt in range(3):
            started = False
            try:
                with self._http.stream("POST", url, params={"alt": "sse"}, headers={"x-goog-api-key": self._key},
                                       json=self._body(system, user, max_tokens)) as r:
                    if r.status_code != 200:
                        r.read()
                        if r.status_code in (429, 500, 503) and attempt < 2:
                            time.sleep(2 * 3 ** attempt)
                            continue
                        raise LLMError(f"Gemini {r.status_code}: {r.text[:300]}", status=r.status_code)
                    finish = None
                    for line in r.iter_lines():
                        if not line.startswith("data:"):
                            continue
                        cand = (json.loads(line[5:]).get("candidates") or [{}])[0]
                        finish = cand.get("finishReason") or finish
                        text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", [])
                                       if not p.get("thought"))
                        if text:
                            started = True
                            yield text
                    if finish == "MAX_TOKENS":
                        raise LLMError("Gemini cevabı çıktı limitinde kesildi")
                    if not started:
                        raise LLMError(f"Gemini boş cevap (finishReason={finish})")
                    return
            except httpx.TimeoutException:
                if started or attempt == 2:
                    raise LLMError("Gemini zaman aşımı") from None
                time.sleep(2 * 3 ** attempt)

    def _parse(self, r) -> str:
        if r.status_code != 200:
            raise LLMError(f"Gemini {r.status_code}: {r.text[:300]}", status=r.status_code)
        cand = r.json().get("candidates", [{}])[0]
        parts = cand.get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        if not text:
            raise LLMError(f"Gemini boş cevap (finishReason={cand.get('finishReason')})")
        if cand.get("finishReason") == "MAX_TOKENS":
            raise LLMError("Gemini cevabı çıktı limitinde kesildi")
        return text.strip()


class OllamaLLM:
    def __init__(self, model: str | None = None, num_ctx: int = 8192, timeout: float = 300):
        self.model = model or config.OLLAMA_MODEL
        self.name = f"ollama:{self.model}"
        self.num_ctx = num_ctx
        self._http = httpx.Client(base_url=config.OLLAMA_HOST, timeout=timeout)

    def generate(self, system: str, user: str, max_tokens: int = 1500) -> str:
        r = self._http.post("/api/chat", json={
            "model": self.model, "stream": False, "think": False,  # qwen3 düşünme modu kapalı: hız + yalın çıktı
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "options": {"temperature": 0, "num_ctx": self.num_ctx, "num_predict": max_tokens},
        })
        if r.status_code != 200:
            raise LLMError(f"Ollama {r.status_code}: {r.text[:300]}")
        return r.json()["message"]["content"].strip()

    def stream(self, system: str, user: str, max_tokens: int = 1500) -> Iterator[str]:
        with self._http.stream("POST", "/api/chat", json={
            "model": self.model, "stream": True, "think": False,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "options": {"temperature": 0, "num_ctx": self.num_ctx, "num_predict": max_tokens},
        }) as r:
            if r.status_code != 200:
                r.read()
                raise LLMError(f"Ollama {r.status_code}: {r.text[:300]}", status=r.status_code)
            for line in r.iter_lines():
                if line:
                    text = json.loads(line).get("message", {}).get("content", "")
                    if text:
                        yield text


class OpenRouterLLM:
    """OpenRouter (OpenAI uyumlu sohbet ucu). Model ZİNCİRİ: ilk model hata verirse (429 kota, 402 kredi, 5xx,
    zaman aşımı, boş cevap) sıradaki denenir — önce ücretsiz model, kotası dolunca ücretli olan.

    Akışta yedek modele yalnız İLK parça gelmeden önce geçilir (yarım cevabın üstüne ikinci model yazmaz).
    Anahtar yalnız Authorization başlığında; isteğe proje/kullanıcı bilgisi eklenmez.
    """
    URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, model: str | None = None, timeout: float = 90):
        self.models = [model] if model else list(config.OPENROUTER_MODELS)
        if not self.models:
            raise LLMError("OpenRouter modeli yok (OPENROUTER_MODELS veya 'openrouter:<model>')")
        self.name = "openrouter:" + self.models[0] + (f" (+{len(self.models) - 1} yedek)" if len(self.models) > 1 else "")
        self._key = os.environ.get("OPENROUTER_API_KEY", "")
        if not self._key:
            raise LLMError("OPENROUTER_API_KEY yok (.env)")
        self._http = httpx.Client(timeout=timeout, headers={"Authorization": f"Bearer {self._key}"})
        self.last_model: str | None = None   # cevabı üreten model (izlenebilirlik)
        self.last_usage: dict | None = None  # {prompt_tokens, completion_tokens, cost}
        # Devre kesici: 429 veren model bir süre atlanır (ücretsiz modelin günlük kotası dolunca her istekte
        # 429 + bekleme + yeniden deneme ~6 sn kaybettiriyordu; ajan soru başına 2-3 çağrı yapar). Ölçüm: KARARLAR.md.
        self._atla: dict[str, float] = {}

    def _aktif(self) -> list[str]:
        now = time.time()
        ms = [m for m in self.models if self._atla.get(m, 0) <= now]
        return ms or list(self.models)   # hepsi atlanmışsa yine de dene (kota açılmış olabilir)

    def _kes(self, model: str, err: "LLMError") -> None:
        if err.status == 429:
            gunluk = "per-day" in str(err) or "per day" in str(err)
            self._atla[model] = time.time() + (3600 if gunluk else 60)

    def _body(self, model: str, system: str, user: str, max_tokens: int, stream: bool) -> dict:
        body = {"model": model, "temperature": 0, "max_tokens": max_tokens, "stream": stream,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "usage": {"include": True},
                # düşünme kapalı: ucuz modellerde düşünme tokenları çıktı limitini tüketip boş cevap döndürüyordu (ölçüldü)
                "reasoning": {"enabled": False}}
        if stream:
            body["stream_options"] = {"include_usage": True}
        return body

    @staticmethod
    def _error(r) -> LLMError:
        try:
            msg = r.json().get("error", {}).get("message", "")
        except ValueError:
            msg = r.text
        return LLMError(f"OpenRouter {r.status_code}: {str(msg)[:300]}", status=r.status_code)

    def generate(self, system: str, user: str, max_tokens: int = 1500) -> str:
        last: Exception | None = None
        for model in self._aktif():
            for attempt in range(2):   # aynı modelde bir kez daha (geçici 429/5xx), sonra sıradaki model
                try:
                    r = self._http.post(self.URL, json=self._body(model, system, user, max_tokens, False))
                except httpx.TimeoutException:
                    last = LLMError(f"OpenRouter zaman aşımı ({model})")
                    break
                if r.status_code == 200:
                    j = r.json()
                    if "error" in j:   # sağlayıcı hatası 200 içinde dönebiliyor
                        last = LLMError(f"OpenRouter sağlayıcı hatası ({model}): {str(j['error'].get('message'))[:200]}",
                                        status=j["error"].get("code") if isinstance(j["error"].get("code"), int) else None)
                        break
                    text = (j["choices"][0]["message"].get("content") or "").strip()
                    if text:
                        self.last_model, self.last_usage = j.get("model", model), j.get("usage")
                        return text
                    last = LLMError(f"OpenRouter boş cevap ({model}, finish={j['choices'][0].get('finish_reason')})")
                    break
                last = self._error(r)
                if r.status_code == 429 and ("per-day" in str(last) or "per day" in str(last)):
                    self._kes(model, last)   # günlük kota: aynı modelde beklemek boşuna
                    break
                if r.status_code not in (429, 500, 502, 503) or attempt == 1:
                    if r.status_code == 429:
                        self._kes(model, last)
                    break
                time.sleep(3)
        raise last or LLMError("OpenRouter: cevap alınamadı")

    def stream(self, system: str, user: str, max_tokens: int = 1500) -> Iterator[str]:
        last: Exception | None = None
        for model in self._aktif():
            started = False
            try:
                with self._http.stream("POST", self.URL, json=self._body(model, system, user, max_tokens, True)) as r:
                    if r.status_code != 200:
                        r.read()
                        last = self._error(r)
                        self._kes(model, last)
                        continue
                    for line in r.iter_lines():
                        if not line.startswith("data:") or line.strip() == "data: [DONE]":
                            continue
                        j = json.loads(line[5:])
                        if "error" in j:
                            raise LLMError(f"OpenRouter akış hatası ({model}): {str(j['error'].get('message'))[:200]}")
                        if j.get("usage"):
                            self.last_usage = j["usage"]
                        text = (j.get("choices") or [{}])[0].get("delta", {}).get("content") or ""
                        if text:
                            started = True
                            yield text
                if started:
                    self.last_model = model
                    return
                last = LLMError(f"OpenRouter boş cevap ({model})")
            except (httpx.TimeoutException, LLMError) as e:
                if started:
                    raise LLMError(f"OpenRouter akışı kesildi ({model})") from None
                last = e if isinstance(e, LLMError) else LLMError(f"OpenRouter zaman aşımı ({model})")
        raise last or LLMError("OpenRouter: cevap alınamadı")


def make_llm(spec: str):
    """'gemini[:model]', 'ollama[:model]', 'openrouter' (OPENROUTER_MODELS zinciri) veya 'openrouter:<model>'"""
    kind, _, model = spec.partition(":")
    if kind == "gemini":
        return GeminiLLM(model or None)
    if kind == "ollama":
        return OllamaLLM(model or None)
    if kind == "openrouter":
        return OpenRouterLLM(model or None)
    raise ValueError(spec)
