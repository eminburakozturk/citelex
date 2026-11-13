"""src.sources.resmigazete ve src.update.erken_uyari birim testleri (ağa çıkmadan çalışır)."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import httpx
import pytest

from src.sources import resmigazete
from src.sources.http import FetchError
from src.update import erken_uyari

FIXTURE = Path(__file__).parent / "fixtures" / "resmigazete_ornek.htm"
FIXTURE_7499 = Path(__file__).parent / "fixtures" / "resmigazete_7499.htm"


def test_ornek_fihrist_ayristirma():
    html_text = FIXTURE.read_bytes().decode("windows-1254")
    records = resmigazete.parse_fihrist(html_text, date(2024, 3, 12))

    # 1 kanun + 18 Cumhurbaşkanı kararı + 2 yönetmelik + 3 yargı kararı = 24; İlân bölümü hariç.
    assert len(records) == 24
    expected_keys = {"tarih", "tur", "baslik", "url", "ilgili_belge_id", "eslesme", "kanit"}
    assert all(set(r.keys()) == expected_keys for r in records)
    assert all(r["tarih"] == "2024-03-12" for r in records)
    assert all("\ufffd" not in r["baslik"] for r in records)
    assert not any(r["baslik"].startswith(("–", "—", "-")) for r in records)
    assert not any("ilanlar/eskiilanlar" in r["url"] for r in records)

    ilk = records[0]
    assert ilk["tur"] == "kanun"
    assert ilk["baslik"].startswith("7499 Ceza Muhakemesi Kanunu")
    assert ilk["url"] == "https://www.resmigazete.gov.tr/eskiler/2024/03/20240312-1.htm"
    assert ilk["ilgili_belge_id"] is None
    assert ilk["eslesme"] is None

    yon = [r for r in records if r["tur"] == "yonetmelik"]
    assert len(yon) == 2
    assert yon[0]["baslik"].startswith("Denizde Çatışmayı Önleme Yönetmeliği")

    kararlar = [r for r in records if r["tur"] == "karar"]
    assert len(kararlar) == 21


def test_derin_katman_eslesmeleri():
    sources = resmigazete.load_sources()

    assert resmigazete.eslesme_bul("6698 Sayılı Kanunda Değişiklik Yapılmasına Dair Kanun", sources) == "kvkk"
    assert resmigazete.eslesme_bul("Kişisel Verilerin Korunması Kanununda Değişiklik", sources) == "kvkk"
    assert resmigazete.eslesme_bul("4857 Sayılı İş Kanununun Bazı Maddelerinde Değişiklik", sources) == "is-kanunu"
    assert resmigazete.eslesme_bul("İŞ KANUNU İLE BAZI KANUNLARDA DEĞİŞİKLİK", sources) == "is-kanunu"
    assert resmigazete.eslesme_bul("6331 Sayılı İş Sağlığı ve Güvenliği Kanununda Değişiklik", sources) == "isg-kanunu"

    # Yönetmelik/tebliğ eşleşmeleri genel "İş Kanunu"ndan önce yakalanmalı.
    assert (
        resmigazete.eslesme_bul(
            "İş Kanununa İlişkin Çalışma Süreleri Yönetmeliğinde Değişiklik Yapılmasına Dair Yönetmelik",
            sources,
        )
        == "calisma-sureleri-yon"
    )
    assert (
        resmigazete.eslesme_bul(
            "Yıllık Ücretli İzin Yönetmeliğinde Değişiklik Yapılmasına Dair Yönetmelik",
            sources,
        )
        == "yillik-izin-yon"
    )
    assert (
        resmigazete.eslesme_bul(
            "Aydınlatma Yükümlülüğünün Yerine Getirilmesinde Uyulacak Usul ve Esaslar Hakkında Tebliğde Değişiklik",
            sources,
        )
        == "aydinlatma-teblig"
    )
    assert (
        resmigazete.eslesme_bul(
            "Kişisel Verilerin Yurt Dışına Aktarılmasına İlişkin Usul ve Esaslar Hakkında Yönetmelikte Değişiklik",
            sources,
        )
        == "yurtdisi-aktarim-yon"
    )


def test_yanlis_pozitif_korumalari():
    sources = resmigazete.load_sources()

    assert resmigazete.eslesme_bul("Deniz İş Kanununda Değişiklik Yapılmasına Dair Kanun", sources) is None
    assert resmigazete.eslesme_bul("Basın İş Kanununda Değişiklik", sources) is None
    assert resmigazete.eslesme_bul("Enerji Piyasası Kurulunun 1475 Sayılı Kararı", sources) is None
    assert resmigazete.eslesme_bul("66980 Sayılı Kanun", sources) is None


def test_teblig_ve_ilgili_isaretleme_sentetik():
    html_sample = """
    <html><body>
      <p><b><u>YÜRÜTME VE İDARE BÖLÜMÜ</u></b></p>
      <p><b><u>TEBLİĞLER</u></b></p>
      <p><a href="20261112-1.htm">–– Aydınlatma Yükümlülüğünün Yerine Getirilmesinde Uyulacak Usul ve Esaslar Hakkında Tebliğde Değişiklik</a></p>
      <p><a href="20261112-2.htm">–– Vergi Usul Kanunu Genel Tebliği (Sıra No: 599)</a></p>
    </body></html>
    """
    recs = resmigazete.parse_fihrist(html_sample, date(2026, 11, 12))
    assert len(recs) == 2
    assert recs[0]["tur"] == "teblig"
    assert recs[0]["ilgili_belge_id"] == "aydinlatma-teblig"
    assert recs[0]["eslesme"] == "baslik"
    assert recs[1]["tur"] == "teblig"
    assert recs[1]["ilgili_belge_id"] is None
    assert recs[1]["eslesme"] is None


def test_torba_kanun_7499_metinden_kvkk_eslesmesi(monkeypatch):
    fihrist_raw = FIXTURE.read_bytes()
    kanun_raw = FIXTURE_7499.read_bytes()

    def _fake_get(url: str, client=None):
        if url.endswith("20240312.htm"):
            return httpx.Response(200, content=fihrist_raw, headers={"content-type": "text/html"}, request=httpx.Request("GET", url))
        if url.endswith("20240312-1.htm"):
            return httpx.Response(200, content=kanun_raw, headers={"content-type": "text/html"}, request=httpx.Request("GET", url))
        raise FetchError(f"404 {url}")

    monkeypatch.setattr(resmigazete, "get", _fake_get)
    recs = resmigazete.kontrol_et(date(2024, 3, 12))

    assert len(recs) == 24
    ilk = recs[0]
    assert ilk["baslik"].startswith("7499 Ceza Muhakemesi Kanunu")
    assert ilk["ilgili_belge_id"] == "kvkk"
    assert ilk["eslesme"] == "metin"
    assert ilk["kanit"] is not None
    assert len(ilk["kanit"]) <= 200
    assert "MADDE 33" in ilk["kanit"]
    assert "6698 sayılı" in ilk["kanit"]


def test_metin_indirme_hatasi_kaydi_dusurmez(monkeypatch):
    html_sample = """
    <html><body>
      <p><b><u>YÜRÜTME VE İDARE BÖLÜMÜ</u></b></p>
      <p><b><u>YÖNETMELİKLER</u></b></p>
      <p><a href="20261112-1.htm">–– Sigorta Yönetmeliğinde Değişiklik Yapılmasına Dair Yönetmelik</a></p>
    </body></html>
    """

    def _fake_get(url: str, client=None):
        if url.endswith("20261112.htm"):
            return httpx.Response(200, content=html_sample.encode("utf-8"), headers={"content-type": "text/html; charset=utf-8"}, request=httpx.Request("GET", url))
        raise FetchError(f"503 {url}")

    monkeypatch.setattr(resmigazete, "get", _fake_get)
    recs = resmigazete.kontrol_et(date(2026, 11, 12))
    assert len(recs) == 1
    assert recs[0]["ilgili_belge_id"] is None
    assert "503" in recs[0]["metin_hatasi"]


def test_metin_eslesme_yanlis_pozitif_ve_isg():
    sources = resmigazete.load_sources()

    sahte_metin = (
        "YÜRÜTME VE İDARE BÖLÜMÜ Sayı: 6331 Karar Sayısı: 6331 "
        "MADDE 1- Bu Yönetmelik uyarınca 6331 TL ödenek ayrılır ve m.6331 uygulanmaz."
    )
    bid, kanit = resmigazete.metin_eslesme_bul(sahte_metin, sources)
    assert bid is None
    assert kanit is None

    gercek_metin = (
        "Dayanak MADDE 2- (1) Bu Yönetmelik, 20/6/2012 tarihli ve 6331 sayılı "
        "İş Sağlığı ve Güvenliği Kanununun 30 uncu maddesine dayanılarak hazırlanmıştır."
    )
    bid2, kanit2 = resmigazete.metin_eslesme_bul(gercek_metin, sources)
    assert bid2 == "isg-kanunu"
    assert kanit2 is not None
    assert len(kanit2) <= 200
    assert "MADDE 2" in kanit2
    assert "6331 sayılı" in kanit2


def test_pdf_metin_okuma(monkeypatch):
    class _FakePage:
        def extract_text(self):
            return "MADDE 4- 4857 sayılı İş Kanununun 41 inci maddesi uyarınca uygulanır."

    class _FakePDF:
        pages = [_FakePage()]

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(resmigazete.pdfplumber, "open", lambda bio: _FakePDF())
    resp = httpx.Response(
        200,
        content=b"%PDF-1.4 fake",
        headers={"content-type": "application/pdf"},
        request=httpx.Request("GET", "https://www.resmigazete.gov.tr/eskiler/2026/11/x.pdf"),
    )
    txt = resmigazete._extract_response_text(resp, "https://www.resmigazete.gov.tr/eskiler/2026/11/x.pdf")
    bid, kanit = resmigazete.metin_eslesme_bul(txt)
    assert bid == "is-kanunu"
    assert "4857 sayılı" in kanit


def test_kontrol_et_basarili_ve_hata(monkeypatch):
    raw = FIXTURE.read_bytes()
    url = "https://www.resmigazete.gov.tr/eskiler/2024/03/20240312.htm"
    fake_resp = httpx.Response(200, content=raw, headers={"content-type": "text/html"}, request=httpx.Request("GET", url))

    monkeypatch.setattr(resmigazete, "get", lambda u, client=None: fake_resp)
    recs = resmigazete.kontrol_et(date(2024, 3, 12), metin_kontrol=False)
    assert len(recs) == 24
    assert recs[0]["baslik"].startswith("7499 Ceza Muhakemesi Kanunu")

    def _raise_block(u, client=None):
        raise FetchError(f"403 {u}")

    monkeypatch.setattr(resmigazete, "get", _raise_block)
    with pytest.raises(FetchError, match="2024-03-12"):
        resmigazete.kontrol_et(date(2024, 3, 12))


def test_erken_uyari_gunluk_ve_tekillestirme(tmp_path, monkeypatch):
    ornek_recs = [
        {
            "tarih": "2024-03-12",
            "tur": "kanun",
            "baslik": "7499 Ceza Muhakemesi Kanunu...",
            "url": "https://www.resmigazete.gov.tr/eskiler/2024/03/20240312-1.htm",
            "ilgili_belge_id": "kvkk",
            "eslesme": "metin",
            "kanit": "MADDE 33- 6698 sayılı...",
        },
        {
            "tarih": "2024-03-12",
            "tur": "yonetmelik",
            "baslik": "İlgisiz Yönetmelik",
            "url": "https://www.resmigazete.gov.tr/eskiler/2024/03/20240312-21.htm",
            "ilgili_belge_id": None,
            "eslesme": None,
            "kanit": None,
        },
    ]

    monkeypatch.setattr(erken_uyari, "kontrol_et", lambda gun, client=None, sources=None: ornek_recs if gun == date(2024, 3, 12) else [])
    log_file = tmp_path / "erken_uyari.jsonl"

    ilk = erken_uyari.kontrol_ve_kaydet(gun_sayisi=2, log_path=log_file, bugun=date(2024, 3, 12))
    assert len(ilk) == 1
    satirlar = [json.loads(s) for s in log_file.read_text(encoding="utf-8").splitlines()]
    assert len(satirlar) == 1
    assert set(satirlar[0].keys()) == {"zaman", "gun", "tur", "baslik", "url", "ilgili_belge_id", "eslesme", "kanit"}
    assert satirlar[0]["ilgili_belge_id"] == "kvkk"

    # İkinci çalıştırmada aynı URL tekrar yazılmamalı.
    ikinci = erken_uyari.kontrol_ve_kaydet(gun_sayisi=2, log_path=log_file, bugun=date(2024, 3, 12))
    assert ikinci == []
    assert len(log_file.read_text(encoding="utf-8").splitlines()) == 1
