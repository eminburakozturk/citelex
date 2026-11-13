"""API testleri: model/Qdrant gerektirmez (sahte Answerer). Çalıştırma: python -m pytest tests -q"""
from __future__ import annotations

import json
import threading

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.ratelimit import RateLimiter
from src.generate.answer import Answerer
from src.generate.llm import LLMError


class Hit:
    def __init__(self, payload):
        self.score, self.payload = 0.9, payload


HITS = [Hit({"atif": "4857 s. İş Kanunu m. 8", "belge_id": "is-kanunu", "belge_tur": "kanun", "madde_no": "8",
             "baslik": "Tanım ve şekil", "metin": "Süresi bir yıl ve daha fazla olan iş sözleşmelerinin yazılı şekilde yapılması zorunludur."})]


class FakeLLM:
    name = "sahte"

    def __init__(self, parts, error=None):
        self.parts, self.error = parts, error

    def generate(self, system, user, max_tokens=1500):
        if self.error:
            raise self.error
        return "".join(self.parts)

    def stream(self, system, user, max_tokens=1500):
        if self.error:
            raise self.error
        yield from self.parts


def make(parts, error=None, top1=0.8) -> Answerer:
    """Gerçek Answerer mantığı (eşik, akış, atıf doğrulama) + sahte arama ve LLM."""
    a = Answerer.__new__(Answerer)
    a.llm, a.cfg, a._lock, a.searcher = FakeLLM(parts, error), {"esik": 0.637, "derlem_tarihi": "2026-11-11"}, threading.Lock(), None
    import src.generate.answer as mod
    mod.build_context = lambda searcher, query, esik, turler=None: (HITS, {"dense_top1": top1, "kanal_top1": {}, "kanallar": ["mevzuat"]})
    return a


def events(text: str) -> list[tuple[str, dict]]:
    out = []
    for blok in text.strip().split("\n\n"):
        ev, data = blok.split("\n", 1)
        out.append((ev.removeprefix("event: "), json.loads(data.removeprefix("data: "))))
    return out


def client(answerer) -> TestClient:
    return TestClient(create_app(answerer))


def test_akis_sirasi_ve_gizli_alanlar():
    with client(make(["Bir yıl ve daha uzun ", "sözleşmeler yazılı yapılır [1]."])) as c:
        r = c.post("/sor", json={"soru": "Hangi sözleşmeler yazılı yapılır?"})
        assert r.status_code == 200 and r.headers["content-type"].startswith("text/event-stream")
        ev = events(r.text)
        assert [e for e, _ in ev] == ["baglam", "parca", "parca", "sonuc"]
        son = ev[-1][1]
        assert son["bilmiyorum"] is False and son["kaynaklar"][0]["anahtar"] == "is-kanunu:8"
        assert "".join(d["metin"] for e, d in ev if e == "parca") == son["cevap"]
        assert "ham" not in son and "esik" not in son and "hukuki tavsiye" in son["uyari"]


def test_cevap_yok_akitilmaz():
    with client(make(["CEVAP", "_YOK\nKaynaklarda uydurma gerekçe."])) as c:
        ev = events(c.post("/sor", json={"soru": "Asgari ücret ne kadar?"}).text)
        assert [e for e, _ in ev] == ["baglam", "sonuc"]
        assert ev[-1][1]["bilmiyorum"] and ev[-1][1]["bilmiyorum_katmani"] == "llm"
        assert "uydurma" not in json.dumps(ev[-1][1], ensure_ascii=False)


def test_atifsiz_cevap_atilir():
    with client(make(["Kaynak göstermeyen bir cevap."])) as c:
        son = events(c.post("/sor", json={"soru": "Bir soru daha?"}).text)[-1][1]
        assert son["bilmiyorum"] and son["bilmiyorum_katmani"] == "atif_dogrulama" and son["kaynaklar"] == []


def test_esik_altinda_llm_cagrilmaz():
    with client(make([], error=AssertionError("LLM çağrılmamalıydı"), top1=0.3)) as c:
        ev = events(c.post("/sor", json={"soru": "Tapu harcı oranı kaçtır?"}).text)
        assert [e for e, _ in ev] == ["sonuc"] and ev[0][1]["bilmiyorum_katmani"] == "arama_esigi"


def test_kota_hatasi_anlasilir_ve_sizdirmaz():
    hata = LLMError("Gemini 429: {\"error\": \"quota for key AIza-GIZLI\"}", status=429)
    with client(make([], error=hata)) as c:
        r = c.post("/sor", json={"soru": "Yıllık izin kaç gün?"})
        ev = events(r.text)
        assert ev[-1][0] == "hata" and "kotası doldu" in ev[-1][1]["mesaj"] and "GIZLI" not in r.text
        r = c.post("/sor?akis=false", json={"soru": "Yıllık izin kaç gün?"})
        assert r.status_code == 503 and "GIZLI" not in r.text


@pytest.mark.parametrize("soru", ["", "ab", "x" * 501])
def test_soru_uzunlugu(soru):
    with client(make(["a [1]"])) as c:
        assert c.post("/sor", json={"soru": soru}).status_code == 422


def test_istek_siniri(monkeypatch):
    monkeypatch.setenv("CITELEX_RATE_DK", "2")
    with client(make(["Cevap [1]."])) as c:
        kodlar = [c.post("/sor?akis=false", json={"soru": "Yıllık izin kaç gün?"}).status_code for _ in range(3)]
        assert kodlar == [200, 200, 429]
        r = c.post("/sor", json={"soru": "Yıllık izin kaç gün?"})
        assert r.status_code == 429 and int(r.headers["retry-after"]) > 0


def test_limiter_pencereleri():
    rl = RateLimiter(per_minute=2, per_day=3, global_per_day=4)
    assert rl.check("a", 0)[0] and rl.check("a", 1)[0]
    assert rl.check("a", 2)[2] == "dakika"
    assert rl.check("a", 61)[0]                    # dakika penceresi açıldı
    assert rl.check("a", 200)[2] == "gunluk"       # günde 3
    assert rl.check("b", 201)[0]                   # başka istemci etkilenmez
    assert rl.check("c", 202)[2] == "gunluk_toplam"
    assert rl.check("c", 86400 + 2)[0]             # ertesi gün


def test_kaynak_anahtari_dogrulanir():
    with client(make(["a [1]"])) as c:
        assert c.get("/kaynak", params={"anahtar": "is-kanunu:8'; DROP"}).status_code == 400


def test_tur_filtresi_dogrulanir():
    with client(make(["Cevap [1]."])) as c:
        assert c.post("/sor?akis=false", json={"soru": "Yıllık izin kaç gün?", "turler": ["kanun"]}).status_code == 200
        assert c.post("/sor?akis=false", json={"soru": "Yıllık izin kaç gün?", "turler": ["roman"]}).status_code == 422
        assert c.post("/sor?akis=false", json={"soru": "Yıllık izin kaç gün?", "turler": []}).status_code == 422


def test_ajan_modu_yeniden_yazip_cevaplar(monkeypatch):
    """İlk denemede CEVAP_YOK -> soru yeniden yazılır -> ikinci denemede atıflı cevap (gerçek LangGraph akışı, sahte LLM)."""
    a = make([])
    cagri = []

    def gen(system, user, max_tokens=1500):
        cagri.append(system[:20])
        if "arama sorgusuna" in system:
            return "4857 sayılı İş Kanunu yazılı sözleşme"
        return "CEVAP_YOK\nyetmiyor" if len(cagri) == 1 else "Yazılı yapılır [1]."
    a.llm.generate = gen
    with client(a) as c:
        r = c.post("/sor?akis=false", json={"soru": "Hangi sözleşmeler yazılı yapılır?", "ajan": True}).json()
    assert r["bilmiyorum"] is False and r["kaynaklar"][0]["anahtar"] == "is-kanunu:8"
    assert r["ajan_sorgular"] == ["4857 sayılı İş Kanunu yazılı sözleşme"] and r["ajan_deneme"] == 2 and len(cagri) == 3


def test_openrouter_devre_kesici(monkeypatch):
    """Günlük kotası dolan ücretsiz model 1 saat atlanır; ikinci istek doğrudan yedek modele gider (bekleme yok)."""
    import httpx
    from src.generate import llm as llm_mod
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    cagri = []

    def handler(req):
        model = json.loads(req.content)["model"]
        cagri.append(model)
        if model == "ucretsiz":
            return httpx.Response(429, json={"error": {"message": "Rate limit exceeded: free-models-per-day"}})
        return httpx.Response(200, json={"model": model, "choices": [{"message": {"content": "tamam"}}]})
    o = llm_mod.OpenRouterLLM()
    o.models = ["ucretsiz", "ucretli"]
    o._http = httpx.Client(transport=httpx.MockTransport(handler))
    assert o.generate("s", "u") == "tamam" and cagri == ["ucretsiz", "ucretli"]
    assert o.generate("s", "u") == "tamam" and cagri == ["ucretsiz", "ucretli", "ucretli"]
