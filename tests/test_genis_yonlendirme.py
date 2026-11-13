"""Geniş katman yönlendirmesi (build_context): eşik, GENIS_FARK ve tür filtresi kuralları — Qdrant/model gerekmez."""
from __future__ import annotations

from src.generate.answer import GENIS_FARK, build_context

ESIK = 0.637


class Hit:
    def __init__(self, score, payload):
        self.score, self.payload = score, payload


def payload(bid, tur="kanun", no="1"):
    return {"belge_id": bid, "belge_tur": tur, "madde_no": no, "atif": f"{bid} m. {no}", "metin": "metin",
            "chunk_id": f"{bid}-{no}"}


class FakeSearcher:
    """search(query, 'dense', top_k=1, belge_tur=...) -> sabit skor; search_context -> sabit bağlam."""

    def __init__(self, mevzuat, karar, genis=None):
        self.skor = {"mevzuat": mevzuat, "karar": karar}
        self.genis = genis

    def search(self, query, method, top_k=1, belge_tur=None):
        kn = "karar" if belge_tur == ["karar"] else "mevzuat"
        return [Hit(self.skor[kn], payload("kvkk" if kn == "mevzuat" else "kvkk-karar-2023-1", "kanun" if kn == "mevzuat" else "karar"))]

    def search_context(self, query, method, max_chars=None, mevzuat_tur=None, **kw):
        return {"mevzuat": [Hit(self.skor["mevzuat"], payload("kvkk"))],
                "karar": [Hit(self.skor["karar"], payload("kvkk-karar-2023-1", "karar"))]}


class FakeGenis:
    def __init__(self, skor):
        self.skor = skor

    def search(self, query, method, top_k=1, belge_tur=None):
        return [Hit(self.skor, payload("kanun-657", no="104"))]

    def search_context(self, query, method, **kw):
        return {"mevzuat": [Hit(self.skor, payload("kanun-657", no="104"))], "karar": []}


def kanal(s, turler=None):
    return build_context(s, "soru", ESIK, turler)[1]["kanallar"]


def test_derin_yeterli_ve_genis_az_onde_derin_kalir():
    assert kanal(FakeSearcher(0.70, 0.40, FakeGenis(0.70 + GENIS_FARK - 0.01))) == ["mevzuat"]


def test_genis_farktan_fazla_onde_genis_secilir():
    assert kanal(FakeSearcher(0.717, 0.40, FakeGenis(0.813))) == ["genis"]   # g13 benzeri


def test_derin_esik_alti_genis_esik_ustu():
    assert kanal(FakeSearcher(0.50, 0.40, FakeGenis(0.70))) == ["genis"]


def test_iki_katman_da_esik_alti_genise_gitmez():
    hits, meta = build_context(FakeSearcher(0.50, 0.40, FakeGenis(0.60)), "soru", ESIK)
    assert meta["kanallar"] != ["genis"] and meta["dense_top1"] < ESIK   # çağıran "bilmiyorum" der


def test_tur_filtresi_kanunu_dislarsa_genis_aranmaz():
    assert kanal(FakeSearcher(0.50, 0.70, FakeGenis(0.90)), ["karar"]) == ["karar"]


def test_genis_yoksa_eski_davranis():
    assert kanal(FakeSearcher(0.70, 0.40)) == ["mevzuat"]
