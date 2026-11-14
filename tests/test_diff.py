"""'Bu madde değişti': kelime farkı, birim eşleştirme, API uçları (ağ/Qdrant gerekmez)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.update import diff
from tests.test_api import client, make


def test_kelime_farki():
    ops = diff.word_diff("ceza 125.000 TL olarak", "ceza 175.000 TL olarak")
    assert ops == [["=", "ceza "], ["-", "125.000"], ["+", "175.000"], ["=", " TL olarak"]]


def test_birim_eslestirme(monkeypatch):
    eski = {"asil:1": {"etiket": "m. 1", "metin": "aynı"}, "asil:2": {"etiket": "m. 2", "metin": "eski hüküm"},
            "asil:3": {"etiket": "m. 3", "metin": "kaldırılan"}}
    yeni = {"asil:1": {"etiket": "m. 1", "metin": "aynı  "}, "asil:2": {"etiket": "m. 2", "metin": "yeni hüküm"},
            "asil:4": {"etiket": "m. 4", "metin": "eklenen"}}
    monkeypatch.setattr(diff, "units", lambda kind, path, bid: eski if str(path) == "a" else yeni)
    out = {b["birim"]: b["durum"] for b in diff.compare("mevzuat", "x", Path("a"), Path("b"))}
    assert out == {"asil:2": "degisti", "asil:3": "silindi", "asil:4": "eklendi"}   # yalnız boşluk farkı sayılmaz


@pytest.fixture
def farklar(tmp_path, monkeypatch):
    fid = "20261112T231623_karar_2023-2007_12-52"
    body = {"fark_id": fid, "zaman": "2026-11-12T23:16:23", "doc_key": "karar:2023-2007", "belge_id": "kvkk-karar-2023-2007",
            "tur": "karar", "eski": {}, "yeni": {}, "ozet": {"degisti": 1},
            "birimler": [{"birim": "hukum", "etiket": "hukum", "durum": "degisti", "eski": "a", "yeni": "b",
                          "fark": [["-", "a"], ["+", "b"]]}]}
    (tmp_path / f"{fid}.json").write_text(json.dumps(body), encoding="utf-8")
    import src.api.app as app_mod
    monkeypatch.setattr(app_mod, "FARK_DIR", tmp_path)
    return fid


def test_api_degisiklikler(farklar):
    with client(make(["x [1]."])) as c:
        r = c.get("/degisiklikler").json()["degisiklikler"]
        assert r[0]["fark_id"] == farklar and "fark" not in r[0]["birimler"][0]   # listede metin yok
        d = c.get(f"/degisiklik/{farklar}").json()
        assert d["birimler"][0]["fark"] == [["-", "a"], ["+", "b"]]
        assert c.get("/degisiklik/..%2F..%2Fetc").status_code in (400, 404)
        assert c.get("/degisiklik/20261112T231623_karar_yok_1-2").status_code == 404


def test_windows_yolu_linuxta_acilir():
    assert diff.yol(r"data\raw\versions\karar_2023-2007\x.txt").as_posix() == "data/raw/versions/karar_2023-2007/x.txt"


def test_deneme_farki_son_degisiklik_sayilmaz(tmp_path, monkeypatch):
    import src.api.app as app_mod
    for i, test in ((1, True), (2, False), (3, True)):
        fid = f"2026111{i}T000000_karar_x_{i}-{i + 1}"
        (tmp_path / f"{fid}.json").write_text(json.dumps({
            "fark_id": fid, "zaman": f"2026-11-1{i}T00:00:00", "doc_key": "karar:x", "belge_id": "x", "tur": "karar",
            "eski": {}, "yeni": {}, "ozet": {}, "birimler": [], "test": test}), encoding="utf-8")
    monkeypatch.setattr(app_mod, "FARK_DIR", tmp_path)
    with client(make(["x [1]."])) as c:
        assert [d["test"] for d in c.get("/degisiklikler").json()["degisiklikler"]] == [True, False, True]
        assert c.get("/guncellik").json()["son_degisiklik"]["fark_id"] == "20261112T000000_karar_x_2-3"
