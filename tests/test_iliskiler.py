"""Tests for src.ingest.iliskiler (history and bidirectional cross-reference extraction)."""
from __future__ import annotations

import json
from pathlib import Path

from src.ingest.iliskiler import (
    build_iliskiler,
    extract_gecmis,
    extract_outgoing_refs,
    parse_degisiklik_notu,
    parse_dipnot,
)


def _make_article(
    belge_id: str,
    madde_no: str,
    metin: str | list[str] = "",
    *,
    belge_tur: str = "kanun",
    degisiklik_notlari: list[str] | None = None,
    dipnotlar: list[dict] | None = None,
) -> dict:
    metinler = [metin] if isinstance(metin, str) else metin
    return {
        "belge_id": belge_id,
        "belge_tur": belge_tur,
        "madde_no": madde_no,
        "fikralar": [{"metin": m} for m in metinler],
        "degisiklik_notlari": degisiklik_notlari or [],
        "dipnotlar": dipnotlar or [],
    }


class TestGecmisParsing:
    def test_kanun_degisik_ek_mulga_khk_aym(self):
        recs, skip = parse_degisiklik_notu("(Değişik: 10/9/2014-6552/5 md.)")
        assert skip == 0
        assert recs == [{"tarih": "2014-09-10", "kanun": "6552 s. Kanun md. 5", "aciklama": "Değişik"}]

        recs_m, _ = parse_degisiklik_notu("(Mülga: 22/5/2003/4857/120 md.)")
        assert recs_m == [{"tarih": "2003-05-22", "kanun": "4857 s. Kanun md. 120", "aciklama": "Mülga"}]

        recs_k, _ = parse_degisiklik_notu("(Değişik: 11/10/2011-KHK-665/28 md.)")
        assert recs_k == [{"tarih": "2011-10-11", "kanun": "665 s. KHK md. 28", "aciklama": "Değişik"}]

        recs_a, _ = parse_degisiklik_notu(
            "(İptal fıkra: Anayasa Mahkemesinin 19/9/2019 tarihli ve E.:2019/42, K.:2019/73 sayılı Kararı ile.)"
        )
        assert recs_a == [{"tarih": "2019-09-19", "kanun": "AYM E.2019/42, K.2019/73", "aciklama": "İptal fıkra"}]

    def test_yonetmelik_rg_note_and_semicolon_multi_event(self):
        recs, skip = parse_degisiklik_notu("(Değişik ibare: RG-18/8/2017-30158)")
        assert skip == 0
        assert recs == [{"tarih": "2017-08-18", "kanun": "RG 30158", "aciklama": "Değişik ibare"}]

        recs_m, skip_m = parse_degisiklik_notu(
            "(Ek cümle: RG-25/8/2017- 30165; Değişik üçüncü fıkra: RG-10/3/2020-31064)"
        )
        assert skip_m == 0
        assert recs_m == [
            {"tarih": "2017-08-25", "kanun": "RG 30165", "aciklama": "Ek cümle"},
            {"tarih": "2020-03-10", "kanun": "RG 31064", "aciklama": "Değişik üçüncü fıkra"},
        ]

    def test_dipnot_with_and_without_article_number(self):
        recs, skip = parse_dipnot(
            "20/6/2012 tarihli ve 6331 sayılı Kanunun 37 nci maddesiyle bu ibare metinden çıkartılmıştır."
        )
        assert skip == 0
        assert recs == [
            {"tarih": "2012-06-20", "kanun": "6331 s. Kanun md. 37", "aciklama": "Yürürlükten kaldırma"}
        ]

        # Madde numarası olmadan "Kanunla" biçimi (ör. 1475/14 dipnotu)
        recs2, skip2 = parse_dipnot(
            "9/8/2002 tarihli ve 4773 sayılı Kanunla bu fıkrada bulunan ibare değiştirilmiştir."
        )
        assert skip2 == 0
        assert recs2 == [
            {"tarih": "2002-08-09", "kanun": "4773 s. Kanun", "aciklama": "İbare/hüküm değişikliği"}
        ]

    def test_dateless_note_skipped_and_counted(self):
        recs, skip = parse_degisiklik_notu("(Değişik ibare: tarihi bilinmeyen not)")
        assert recs == []
        assert skip == 1

        recs_d, skip_d = parse_dipnot("Yayımlanan yönetmelik hükmü uyarınca uygulanır.")
        assert recs_d == []
        assert skip_d == 1

    def test_extract_gecmis_sorted_and_deduplicated(self):
        art = _make_article(
            "is-kanunu",
            "30",
            degisiklik_notlari=[
                "(Ek cümle: 31/7/2008-5797/10 md.)",
                "(Değişik: 15/5/2008-5763/2 md.)",
            ],
            dipnotlar=[
                {"no": 1, "metin": "15/5/2008 tarihli ve 5763 sayılı Kanunun 2 nci maddesiyle değiştirilmiştir."},
                {"no": 2, "metin": "25/4/2013 tarihli ve 6462 sayılı Kanunun 1 inci maddesiyle başlığı değiştirilmiştir."},
            ],
        )
        gecmis, skipped = extract_gecmis(art)
        assert skipped == 0
        assert [g["tarih"] for g in gecmis] == ["2008-05-15", "2008-07-31", "2013-04-25"]
        assert gecmis[2]["aciklama"] == "Başlık değişikliği"


class TestIliskiExtraction:
    VALID = {
        "is-kanunu:3",
        "is-kanunu:5",
        "is-kanunu:7",
        "is-kanunu:17",
        "is-kanunu:20",
        "is-kanunu:25",
        "is-kanunu:53",
        "is-kanunu:63",
        "is-kanunu:71",
        "is-kanunu:Ek 2",
        "is-kanunu:Geçici 4",
        "is-kanunu:106",
        "kvkk:5",
        "kvkk:6",
        "kvkk:11",
        "kvkk:13",
        "kvkk:22",
        "isg-kanunu:7",
        "isg-kanunu:32",
        "yurtdisi-aktarim-yon:11",
        "imha-yon:12",
        "yillik-izin-yon:7",
    }
    BASE_MAP = {
        "yurtdisi-aktarim-yon": "kvkk",
        "imha-yon": "kvkk",
        "yillik-izin-yon": "is-kanunu",
    }

    def test_same_doc_and_cross_doc_patterns(self):
        art = _make_article(
            "is-kanunu",
            "99",
            (
                "Bu Kanunun 5 inci maddesinde öngörülen ilkeler, 17 nci madde ve 53 üncü maddede "
                "yer alan hükümler ile ek 2 nci ve geçici 4 üncü maddeler ve 6698 sayılı Kanunun "
                "6 ncı maddesi birlikte değerlendirilir."
            ),
        )
        refs = extract_outgoing_refs(art, self.VALID, self.BASE_MAP)
        assert refs == [
            "is-kanunu:5",
            "is-kanunu:17",
            "is-kanunu:53",
            "is-kanunu:Ek 2",
            "is-kanunu:Geçici 4",
            "kvkk:6",
        ]

    def test_dayanak_base_kanun_with_capitalized_sentence_and_inline_annot(self):
        yon = _make_article(
            "yurtdisi-aktarim-yon",
            "11",
            "d) Kişisel verileri aktarılan ilgili kişilerin Kanunun 11 inci maddesinde belirtilen hakları saklıdır.",
            belge_tur="yonetmelik",
        )
        assert extract_outgoing_refs(yon, self.VALID, self.BASE_MAP) == ["kvkk:11"]

        imha = _make_article(
            "imha-yon",
            "12",
            "(1) İlgili kişi, Kanunun (Değişik ibare:RG-28/4/2019-30758) 11 inci ve 13 üncü maddelerine istinaden başvurur.",
            belge_tur="yonetmelik",
        )
        assert extract_outgoing_refs(imha, self.VALID, self.BASE_MAP) == ["kvkk:11", "kvkk:13"]

        dayanak = _make_article(
            "imha-yon",
            "3",
            "(1) Bu Yönetmelik, 6698 sayılı Kanunun 7 nci maddesinin üçüncü fıkrası ile 22 nci maddesinin (e) bendine dayanır.",
            belge_tur="yonetmelik",
        )
        # 7 corpus içinde olmadığı için atlanır, aynı cümledeki 22 yakalanır
        assert extract_outgoing_refs(dayanak, self.VALID, self.BASE_MAP) == ["kvkk:22"]

    def test_bent_list_cross_law_amendment_and_quote_suppression(self):
        art = _make_article(
            "isg-kanunu",
            "32",
            (
                "22/5/2003 tarihli ve 4857 sayılı İş Kanununun;\n"
                "a) 7 nci maddesinin son cümlesi değiştirilmiştir.\n"
                "b) 25 inci maddesinin bendinde yer alan “veya 84 üncü maddeye aykırı hareket etmesi” ibaresi çıkarılmıştır.\n"
                "c) 71 inci maddesinin fıkrası güncellenmiştir."
            ),
        )
        refs = extract_outgoing_refs(art, self.VALID | {"is-kanunu:84", "isg-kanunu:25"}, self.BASE_MAP)
        assert refs == ["is-kanunu:7", "is-kanunu:25", "is-kanunu:71"]

    def test_false_positives_and_external_laws_ignored(self):
        art = _make_article(
            "is-kanunu",
            "5",
            (
                "5 inci fıkra ve 1 inci sırada sayılan hallerde 3 üncü ay sonunda kimyasal madde kullanılır. "
                "506 Sayılı Kanunun 7 nci veya aynı Kanunun Geçici 4 üncü maddesi ile "
                "2821 sayılı Sendikalar Kanununun 31 inci maddesi hükümleri saklıdır. "
                "20 nci madde hükümleri uygulanır. 999 uncu madde derlem dışıdır."
            ),
        )
        refs = extract_outgoing_refs(art, self.VALID, self.BASE_MAP)
        assert refs == ["is-kanunu:20"]

    def test_build_iliskiler_bidirectional_symmetry(self, tmp_path: Path):
        articles_path = tmp_path / "articles.jsonl"
        sources_path = tmp_path / "sources.json"
        out_path = tmp_path / "iliskiler.json"

        sample_articles = [
            _make_article("kvkk", "5", "Genel şartlar."),
            _make_article("kvkk", "6", "5 inci madde saklıdır."),
            _make_article(
                "yurtdisi-aktarim-yon",
                "10",
                "Kanunun 5 inci ve 6 ncı maddelerinde belirtilen şartlar uygulanır.",
                belge_tur="yonetmelik",
            ),
        ]
        articles_path.write_text(
            "\n".join(json.dumps(a, ensure_ascii=False) for a in sample_articles) + "\n",
            encoding="utf-8",
        )
        sources_path.write_text(
            json.dumps(
                {
                    "yurtdisi": {
                        "belge_id": "yurtdisi-aktarim-yon",
                        "dayanak": "6698 sayılı Kanunun 9 uncu maddesi",
                    }
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        data, stats = build_iliskiler(articles_path=articles_path, sources_path=sources_path, out_path=out_path)
        assert out_path.is_file()
        assert stats["yonlu_iliski"] == 3
        assert yalin(data["yurtdisi-aktarim-yon:10"]["iliskili"]) == [
            {"anahtar": "kvkk:5", "iliski": "atif_yapar"},
            {"anahtar": "kvkk:6", "iliski": "atif_yapar"},
        ]
        assert yalin(data["kvkk:5"]["iliskili"]) == [
            {"anahtar": "kvkk:6", "iliski": "atif_alir"},
            {"anahtar": "yurtdisi-aktarim-yon:10", "iliski": "atif_alir"},
        ]
        assert yalin(data["kvkk:6"]["iliskili"]) == [
            {"anahtar": "kvkk:5", "iliski": "atif_yapar"},
            {"anahtar": "yurtdisi-aktarim-yon:10", "iliski": "atif_alir"},
        ]


def yalin(iliskili: list[dict]) -> list[dict]:
    """Karşılaştırma için anahtar + ilişki; atıf alanı her öğede bulunmalı."""
    assert all("atif" in x and "baslik" in x for x in iliskili)
    return [{"anahtar": x["anahtar"], "iliski": x["iliski"]} for x in iliskili]
