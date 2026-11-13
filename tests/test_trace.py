"""İz kaydı: her soru için tek satır (cevap, eşik reddi, LLM hatası; akışlı ve akışsız)."""
from __future__ import annotations

import json

import pytest

from src.generate.llm import LLMError
from tests.test_api import client, make


def oku(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]


@pytest.fixture
def iz(tmp_path, monkeypatch):
    p = tmp_path / "izler.jsonl"
    monkeypatch.setenv("CITELEX_IZ_DOSYA", str(p))
    return p


def test_akisli_cevap_izi(iz):
    a = make(["Yazılı yapılır [1]."])
    a.llm.last_usage, a.llm.last_model = None, "sahte-model"
    with client(a) as c:
        c.post("/sor", json={"soru": "Hangi sözleşmeler yazılı yapılır?"})
    (r,) = oku(iz)
    assert r["akis"] is True and r["sonuc"] == "cevap" and r["atif"] == ["is-kanunu:8"]
    assert r["baglam"] == ["is-kanunu:8"] and r["model"] == "sahte-model"
    assert r["arama_sn"] is not None and r["llm_sn"] is not None and r["toplam_sn"] >= 0


def test_esik_reddi_ve_hata_izi(iz):
    with client(make(["x"], top1=0.1)) as c:
        c.post("/sor?akis=false", json={"soru": "Bugün hava nasıl olacak?"})
    with client(make([], error=LLMError("OpenRouter 429", status=429))) as c:
        c.post("/sor", json={"soru": "Hangi sözleşmeler yazılı yapılır?"})
    r1, r2 = oku(iz)
    assert r1["sonuc"] == "bilmiyorum" and r1["bilmiyorum_katmani"] == "arama_esigi" and r1["llm_sn"] is None
    assert r2["sonuc"] == "hata" and "429" in r2["hata"]


def test_ajan_izi(iz):
    a = make(["Yazılı yapılır [1]."])
    with client(a) as c:
        c.post("/sor?akis=false", json={"soru": "Hangi sözleşmeler yazılı yapılır?", "ajan": True})
    (r,) = oku(iz)
    assert r["sonuc"] == "cevap" and r["atif"] == ["is-kanunu:8"]


def test_ajan_varsayilani_ortamdan(monkeypatch):
    from src.api.app import Soru
    monkeypatch.setenv("CITELEX_AJAN", "1")
    assert Soru(soru="abc").ajan is True
    monkeypatch.setenv("CITELEX_AJAN", "0")
    assert Soru(soru="abc").ajan is False and Soru(soru="abc", ajan=True).ajan is True
