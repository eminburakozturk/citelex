"""src.ingest.parse_hf birim testleri."""
from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path

from src.ingest import parse as deep_parse
from src.ingest import parse_hf


def test_alan_adlari_article_ile_uyumlu():
    deep_fields = {f.name for f in fields(deep_parse.Article) if not f.name.startswith("_")}
    hf_fields = {f.name for f in fields(parse_hf.Article)}
    assert hf_fields == deep_fields


def test_madde_varyantlari_ve_fikra_ayristirma():
    text = (
        "ÖRNEK KANUN Kanun Numarası : 9999 Kabul Tarihi : 1/1/2025 "
        "Yayımlandığı Resmî Gazete : Tarih: 2/1/2025 Sayı: 32000 "
        "BİRİNCİ BÖLÜM Genel Hükümler. Amaç ve kapsam "
        "MADDE 1- (1) Birinci fıkra metnidir. (2) İkinci fıkra (1) numaralı bende atıf yapar. "
        "Yetki "
        "Madde 2 – İlk cümle devam eder. "
        "Ara hüküm "
        "MADDE 2/A − (1) Eksi işareti ile ayrılan madde. "
        "MADDE 3 ‒ (Mülga: 12/3/2024-7499/1 md.) "
        "Ek Madde 2 – (Değişik: 1/2/2024-7500/2 md.) Ek madde metni. "
        "Geçici Madde 1. – Geçici madde metni. "
        "Mükerrer Madde 8 [1] Mükerrer madde metni. "
        "9999 SAYILI KANUNA EK VE DEĞİŞİKLİK GETİREN MEVZUATIN LİSTESİ Geçici Madde 99 1/1/2026"
    )
    arts = parse_hf.parse_law_text(text, "9999", "kanun-9999")
    assert [a.madde_no for a in arts] == ["1", "2", "2/A", "3", "Ek 2", "Geçici 1", "Mükerrer 8"]
    assert [a.madde_tur for a in arts] == ["asil", "asil", "asil", "asil", "ek", "gecici", "asil"]

    assert arts[0].belge_adi == "ÖRNEK KANUN"
    assert arts[0].sayfa is None
    assert "BİRİNCİ BÖLÜM" in arts[0].bolum
    assert arts[0].baslik == "Amaç ve kapsam"
    assert [f["fikra_no"] for f in arts[0].fikralar] == [1, 2]
    assert all(f["numara_kaynagi"] == "metin" for f in arts[0].fikralar)

    assert arts[1].baslik == "Yetki"
    assert arts[1].fikralar[0]["numara_kaynagi"] == "sira"

    assert arts[3].mulga is True
    assert arts[4].degisiklik_notlari == ["(Değişik: 1/2/2024-7500/2 md.)"]


def test_tirnak_ici_alinti_madde_bolmez_ve_paragraf_fikra():
    text = (
        "TORBA KANUN Kanun Numarası : 9998 Kabul Tarihi : 1/1/2025 "
        "Yayımlandığı Resmî Gazete : Tarih: 2/1/2025 Sayı: 32001 "
        "MADDE 1- 6698 sayılı Kanunun 9 uncu maddesi değiştirilmiştir. "
        "“MADDE 9- (1) Alıntı madde bölünmemelidir.” "
        "MADDE 2-\nBirinci paragraf:\na) İlk bent;\nb) İkinci bent.\n\nİkinci paragraf burada başlar. "
        "MADDE 3- (1) Aktif fıkra. (2) (Mülga: 1/1/2024-7499/5 md.) "
        "MADDE 4- (1/1/2024 tarihli kanun ile ilgili olup yerine işlenmiştir.)"
    )
    arts = parse_hf.parse_law_text(text, "9998", "kanun-9998")
    assert [a.madde_no for a in arts] == ["1", "2", "3", "4"]
    assert "Alıntı madde bölünmemelidir" in arts[0].fikralar[0]["metin"]
    assert len(arts[1].fikralar) == 2
    assert "a) İlk bent;" in arts[1].fikralar[0]["metin"]
    assert arts[2].fikralar[0]["mulga"] is False
    assert arts[2].fikralar[1]["mulga"] is True
    assert arts[3].diger_kanuna_islendi is True


def test_parse_all_derin_atla_ve_tertip(tmp_path: Path):
    hf_dir = tmp_path / "hf"
    hf_dir.mkdir()
    # Derin katman atlanmalı
    (hf_dir / "6698.json").write_text(
        json.dumps({"law_number": 6698, "text": "KVKK Kanun Numarası : 6698 MADDE 1- (1) Test."}, ensure_ascii=False),
        encoding="utf-8",
    )
    # Geniş katman ve tertip kopyası
    (hf_dir / "657.json").write_text(
        json.dumps({"law_number": 657, "text": "DMK Kanun Numarası : 657 MADDE 1- İlk. MADDE 3- Üçüncü."}, ensure_ascii=False),
        encoding="utf-8",
    )
    (hf_dir / "657_t3.json").write_text(
        json.dumps({"law_number": 657, "text": "ESKİ Kanun Numarası : 657 Madde 1 – Eski metin."}, ensure_ascii=False),
        encoding="utf-8",
    )

    out_jsonl = tmp_path / "articles_genis.jsonl"
    rapor_md = tmp_path / "rapor.md"
    res = parse_hf.parse_all(hf_dir=hf_dir, out_path=out_jsonl, report_path=rapor_md, seed=7)

    assert res["atlanan_derin"] == ["6698"]
    assert res["kanun_sayisi"] == 2
    assert res["toplam_madde"] == 3
    assert res["numara_atlamali_kanun"] == 1

    rows = [json.loads(line) for line in out_jsonl.read_text(encoding="utf-8").splitlines()]
    assert {r["belge_id"] for r in rows} == {"kanun-657", "kanun-657-t3"}
    assert "kanun-657" in rapor_md.read_text(encoding="utf-8")


def test_ek_liste_ayirma_ve_uzun_liste_bolme():
    satirlar = " ".join(f"{i} ANKARA KURUM-{i} ÖZEL HASTANESİ VE MERKEZİ;" for i in range(1, 120))
    text = (
        "OHAL KANUNU Kanun Numarası : 6749 Kabul Tarihi : 18/10/2016 "
        "Yayımlandığı Resmî Gazete : Tarih : 29/10/2016 Sayı : 29872 "
        "Yayımlandığı Düstur : Tertip : 5 Cilt : 58 "
        "MADDE 11- Yürürlük maddesi. "
        "MADDE 12- (1) Bu Kanun hükümlerini Bakanlar Kurulu yürütür. "
        f"I SAYILI LİSTE [6] {satirlar} "
        "EK-1 Kısa cetvel satırı: 1) Kalem A; 2) Kalem B."
    )
    arts = parse_hf.parse_law_text(text, "6749", "kanun-6749")
    assert [a.madde_tur for a in arts] == ["asil", "asil", "ek_liste", "ek_liste"]
    assert arts[1].madde_no == "12"
    assert "I SAYILI LİSTE" not in arts[1].fikralar[0]["metin"]
    assert arts[2].madde_no == "I Sayılı Liste"
    assert len(arts[2].fikralar) >= 3
    assert all("I Sayılı Liste" in f["metin"] for f in arts[2].fikralar)
    assert all(len(f["metin"]) <= 1500 for f in arts[2].fikralar)
    assert arts[3].madde_no == "EK-1"
    assert "EK-1" in arts[3].fikralar[0]["metin"]


def test_baslik_dustur_bolum_temizligi_ve_dipnot_sonrasi_fikra():
    uzun_govde = " ".join(
        f"({chr(97 + (i % 20))}) Bend {i}: uzun açıklama metni ve detaylı düzenleme burada yer alır;"
        for i in range(60)
    )
    text = (
        "DENEME KANUNU Kanun Numarası : 4787 Kabul Tarihi : 9/1/2003 "
        "Yayımlandığı Resmî Gazete : Tarih : 18/1/2003 Sayı : 24997 "
        "Yayımlandığı Düstur : Tertip : Cilt : 7 Amaç ve kapsam "
        "MADDE 1- (1) İlk fıkra bitti. [10] (2) Dipnottan sonra gelen ikinci fıkra. "
        "BÖLÜM : II İkinci Bölüm Başlığı Madde başlığı buraya: "
        f"MADDE 2- (1) Bu Kanunun uygulanmasında; {uzun_govde}"
    )
    arts = parse_hf.parse_law_text(text, "4787", "kanun-4787")
    assert len(arts) == 2
    assert arts[0].baslik == "Amaç ve kapsam"
    assert "Tertip" not in arts[0].baslik and "Cilt" not in arts[0].baslik
    assert [f["fikra_no"] for f in arts[0].fikralar] == [1, 2]
    assert "BÖLÜM" in arts[1].bolum
    assert "BÖLÜM" not in arts[1].baslik
    assert "\n" in arts[1].fikralar[0]["metin"]
