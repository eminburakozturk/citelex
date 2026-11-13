"""src.sources.resmigazete birim testleri (ağa çıkmadan çalışır)."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import httpx
import pytest

from src.sources import resmigazete
from src.sources.http import FetchError

FIXTURE = Path(__file__).parent / "fixtures" / "resmigazete_ornek.htm"


def test_ornek_fihrist_ayristirma():
    html_text = FIXTURE.read_bytes().decode("windows-1254")
    records = resmigazete.parse_fihrist(html_text, date(2024, 3, 12))

    # 1 kanun + 18 Cumhurbaşkanı kararı + 2 yönetmelik + 3 yargı kararı = 24; İlân bölümü hariç.
    assert len(records) == 24
    assert all(set(r.keys()) == {"tarih", "tur", "baslik", "url", "ilgili_belge_id"} for r in records)
    assert all(r["tarih"] == "2024-03-12" for r in records)
    assert all("\ufffd" not in r["baslik"] for r in records)
    assert not any(r["baslik"].startswith(("–", "—", "-")) for r in records)
    assert not any("ilanlar/eskiilanlar" in r["url"] for r in records)

    ilk = records[0]
    assert ilk["tur"] == "kanun"
    assert ilk["baslik"].startswith("7499 Ceza Muhakemesi Kanunu")
    assert ilk["url"] == "https://www.resmigazete.gov.tr/eskiler/2024/03/20240312-1.htm"
    assert ilk["ilgili_belge_id"] is None

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
    assert recs[1]["tur"] == "teblig"
    assert recs[1]["ilgili_belge_id"] is None


def test_kontrol_et_basarili_ve_hata(monkeypatch):
    raw = FIXTURE.read_bytes()
    url = "https://www.resmigazete.gov.tr/eskiler/2024/03/20240312.htm"
    fake_resp = httpx.Response(200, content=raw, headers={"content-type": "text/html"}, request=httpx.Request("GET", url))

    monkeypatch.setattr(resmigazete, "get", lambda u, client=None: fake_resp)
    recs = resmigazete.kontrol_et(date(2024, 3, 12))
    assert len(recs) == 24
    assert recs[0]["baslik"].startswith("7499 Ceza Muhakemesi Kanunu")

    def _raise_block(u, client=None):
        raise FetchError(f"403 {u}")

    monkeypatch.setattr(resmigazete, "get", _raise_block)
    with pytest.raises(FetchError, match="2024-03-12"):
        resmigazete.kontrol_et(date(2024, 3, 12))
