"""Arayüz yardımcı uçları: adimlar, /aciklama (önbellek), /ilgili (eşik süzgeci), /guncellik — model/Qdrant gerekmez."""
from __future__ import annotations

import json

import src.tools as tools
from src.generate import yardimci
from src.generate.answer import adimlar
from tests.test_api import client, make

MADDE = {"anahtar": "is-kanunu:53", "atif": "4857 s. İş Kanunu m. 53", "baslik": "Yıllık ücretli izin",
         "parcalar": [{"fikra_no": 1, "metin": "En az bir yıl çalışana izin verilir.", "mulga": False}]}


class LLM:
    name = "sahte"

    def __init__(self, out):
        self.out, self.n = out, 0

    def generate(self, system, user, max_tokens=1500):
        self.n += 1
        return json.dumps(self.out, ensure_ascii=False)


def test_adimlar_cevap_ve_ajan():
    a = {"kanallar": ["mevzuat"], "baglam_anahtar": ["a:1", "a:2"], "arama_sn": 0.1, "llm_sn": 2.0,
         "kaynaklar": [{"no": 1}], "gecersiz_atif": [], "ajan_deneme": 2, "ajan_sorgular": ["yeni sorgu"],
         "bilmiyorum_katmani": None}
    ad = [x["ad"] for x in adimlar(a)]
    assert ad == ["arama", "esik", "yeniden_yazma", "llm", "atif_dogrulama"]
    assert all(x["durum"] == "tamam" for x in adimlar(a))


def test_adimlar_esik_reddi():
    r = adimlar({"kanallar": ["mevzuat"], "baglam_anahtar": [], "bilmiyorum_katmani": "arama_esigi"})
    assert [x["ad"] for x in r] == ["arama", "esik"] and r[1]["durum"] == "basarisiz"


def test_aciklama_onbellek():
    yardimci._aciklama_cache.d.clear()
    llm = LLM({"maddeler": ["Bir yıl çalışan izin alır."], "ornek": None})
    r1 = yardimci.aciklama(llm, MADDE)
    r2 = yardimci.aciklama(llm, MADDE)
    assert r1 == r2 and llm.n == 1 and "hukuki tavsiye" in r1["uyari"].lower()


class Hit:
    def __init__(self, score):
        self.score = score


class Searcher:
    def search(self, q, method, top_k=1, belge_tur=None):
        return [Hit(0.8 if "z" in q else 0.3)]


def test_ilgili_derlem_disi_soru_onerilmez():
    yardimci._ilgili_cache.d.clear()
    llm = LLM({"sorular": ["İzin bölünebilir mi?", "Bitcoin fiyatı ne olur?", "Yol izni var mı?"]})
    out = yardimci.ilgili_sorular(llm, Searcher(), "Yıllık izin kaç gün?", ["is-kanunu:53"], 0.637)
    assert out == ["İzin bölünebilir mi?", "Yol izni var mı?"]


def test_api_aciklama_ve_guncellik(monkeypatch):
    yardimci._aciklama_cache.d.clear()
    monkeypatch.setattr(tools, "madde_getir", lambda s, k, *a: MADDE)
    a = make([])
    a.llm.generate = lambda *x, **k: json.dumps({"maddeler": ["Açıklama."], "ornek": "Örnek."})
    with client(a) as c:
        r = c.post("/aciklama", json={"anahtar": "is-kanunu:53"}).json()
        assert r["maddeler"] == ["Açıklama."] and r["ornek"] == "Örnek."
        g = c.get("/guncellik").json()
        assert set(g) == {"son_kontrol", "belge_sayisi", "rg_bekleyen", "son_degisiklik"}


def test_api_sonuc_adimlar():
    with client(make(["Yazılı yapılır [1]."])) as c:
        r = c.post("/sor?akis=false", json={"soru": "Hangi sözleşmeler yazılı yapılır?"}).json()
    assert [x["ad"] for x in r["adimlar"]][-1] == "atif_dogrulama" and "model" in r
