"""LLM istemcileri: Gemini (API) ve Ollama (yerel). İkisi de generate(system, user) -> str.

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
            time.sleep(2 * 3 ** attempt)
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


def make_llm(spec: str):
    """'gemini', 'gemini:<model>', 'ollama', 'ollama:<model>'"""
    kind, _, model = spec.partition(":")
    if kind == "gemini":
        return GeminiLLM(model or None)
    if kind == "ollama":
        return OllamaLLM(model or None)
    raise ValueError(spec)
