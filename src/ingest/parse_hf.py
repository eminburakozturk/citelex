"""Hugging Face turkish-legislation-corpus (data/raw/hf_corpus/*.json) ayrıştırıcısı.

Kanun metinlerini src/ingest/parse.py'deki Article şemasıyla uyumlu JSONL biçimine
çevirir (data/processed/articles_genis.jsonl) ve kalite raporunu üretir.
Derin katmandaki kanunlar (6698, 4857, 6331, 1475) mevzuat.gov.tr PDF'lerinden
alındığı için burada atlanır.

Kullanım:
  python -m src.ingest.parse_hf
  python -m src.ingest.parse_hf --rapor results/genis_katman_rapor.md
"""
from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

HF_DIR = Path("data/raw/hf_corpus")
OUT_PATH = Path("data/processed/articles_genis.jsonl")
REPORT_PATH = Path("results/genis_katman_rapor.md")

SKIP_LAWS = {"6698", "4857", "6331", "1475"}

_DASHES = r"\-\u2013\u2014\u2012\u2212"  # -, –, —, ‒, −

# Madde başlığı: "MADDE 5 –", "Madde 1 ilâ 4 –", "Ek Madde 2-", "Geçici Madde 1. –", "Mükerrer Madde 44 [1]"
RE_MADDE = re.compile(
    rf"(?<![\"“'\wçğıöşüÇĞİÖŞÜ])"
    rf"(?P<tur>(?:EK\s+GEÇİCİ|Ek\s+Geçici|EK|Ek|ek|GEÇİCİ|Geçici|geçici|MÜKERRER|Mükerrer|mükerrer)\s+)?"
    rf"(?P<kw>MADDE|Madde|madde)\s+"
    rf"(?P<no>\d+(?:\s*/\s*[A-ZÇĞİÖŞÜ](?![A-Za-zçğıöşüÇĞİÖŞÜ]))?)"
    rf"(?:(?:\s+(?:il[aâ])\s+|\s*[{_DASHES}]\s*)(?P<no_end>\d+)(?=\s*(?:\.|\[|[{_DASHES}])))?"
    rf"\s*(?:\.)?(?:\s*\[\d+\])*\s*"
    rf"(?=[{_DASHES}]|(?<=\]))",
)
RE_LEADING_SEP = re.compile(rf"^[{_DASHES}\s.]+")
RE_FIKRA_NO = re.compile(r"^\((?P<n>\d+)\)\s*")
RE_FIKRA_SPLIT = re.compile(r"(?:^|(?<=[\.\)\”\"])\s+)\((\d+)\)\s+(?=[A-ZÇĞİÖŞÜa-zçğıöşü0-9\(\“\"])")
RE_BENT = re.compile(r"^([a-zçğıöşü]{1,2}\)|\([IVX]+\)|[IVX]+\s*[-–.]\s|\([a-zçğıöşü]\)\s|\d+\.\s|[a-zçğıöşü]\.\s)")
RE_ANNOT = re.compile(r"\((?:[^()]*?)(?:Ek|Değişik|Mülga|İptal|Başlığı|Yeniden)[^()]*?\)")
RE_MULGA_FULL = re.compile(r"^(?:\([^)]*Mülga[^)]*\)|Mülga\s*:[^.]*)\s*\.?\s*$", re.I)
RE_ISLENDI = re.compile(r"^\(?.*ilgili olup.*yer(?:ler)?ine işlenmiştir\.?\)?\s*$", re.S | re.I)
RE_KUNYE_END = re.compile(
    r"(?P<adi>.+?)\s+(?:Kanun(?:un|u)?|Kabul)?\s*(?:Numarası|Maddesi)\s*:\s*\d+.*?"
    r"(?:Yayımlandığı\s+Düstur\s*:[^\n]*?(?:Sayfa\s*:\s*\d+|Cilt\s*:\s*\d+|Tertip\s*:\s*\d+)|"
    r"Yayımlandığı\s+Resmî\s+Gazete\s*:[^\n]*?Sayı\s*:\s*\d+)",
    re.I,
)
RE_END_MARKERS = re.compile(
    r"\b\d+\s+SAYILI\s+KANUNA\s+EK\s+VE\s+DEĞİŞİKLİK\b|"
    r"\bİŞLENEMEYEN\s+HÜKÜMLER\b|"
    r"\bSAYILI\s+CETVEL\b",
    re.I,
)
RE_BOLUM_HEADER = re.compile(
    r"((?:BİRİNCİ|İKİNCİ|ÜÇÜNCÜ|DÖRDÜNCÜ|BEŞİNCİ|ALTINCI|YEDİNCİ|SEKİZİNCİ|DOKUZUNCU|ONUNCU|"
    r"ONBİRİNCİ|ONİKİNCİ)\s+(?:KISIM|BÖLÜM)\b[^.]*)"
)
RE_TAIL_FOOTNOTES = re.compile(r"(?<=\.)\s+(?=\[1\]\s)")


@dataclass
class Article:
    belge_id: str
    belge_tur: str
    belge_no: str
    belge_adi: str
    kisa_ad: str
    madde_tur: str
    madde_no: str
    baslik: str
    bolum: str
    sayfa: int | None
    mulga: bool = False
    diger_kanuna_islendi: bool = False
    degisiklik_notlari: list[str] = field(default_factory=list)
    fikralar: list[dict] = field(default_factory=list)
    dipnotlar: list[dict] = field(default_factory=list)


def _norm(s: str) -> str:
    return re.sub(r"[ \t\u00a0]+", " ", s).strip()


def _extract_title_and_body(text: str, law_no: str) -> tuple[str, str]:
    m = RE_KUNYE_END.match(text)
    if m:
        adi = re.sub(r"\s*\[\d+\]\s*", " ", m.group("adi")).strip(" -–—:")
        return _norm(adi) or f"{law_no} Sayılı Kanun", text[m.end():].strip()

    # Künye kalıbı standart değilse ilk "Numarası" veya "MADDE" öncesi kısmı al
    m_no = re.search(r"^(?P<adi>.+?)\s+(?:Kanun(?:un|u)?|Kabul)?\s*(?:Numarası|Maddesi)\s*:", text, re.I)
    if m_no:
        adi = re.sub(r"\s*\[\d+\]\s*", " ", m_no.group("adi")).strip(" -–—:")
        return _norm(adi) or f"{law_no} Sayılı Kanun", text

    return f"{law_no} Sayılı Kanun", text


def _belge_id_from_path(path: Path, law_no: str) -> str:
    stem = path.stem
    if "_t" in stem:
        tertip = stem.split("_t", 1)[1]
        return f"kanun-{law_no}-t{tertip}"
    return f"kanun-{law_no}"


def _madde_tur_ve_no(tur_prefix: str | None, no: str) -> tuple[str, str]:
    clean_no = re.sub(r"\s+", "", no)
    if not tur_prefix:
        return "asil", clean_no
    p = tur_prefix.strip().upper().replace("İ", "I")
    if "GEÇ" in p or "GEC" in p:
        if "EK" in p:
            return "gecici", f"Ek Geçici {clean_no}"
        return "gecici", f"Geçici {clean_no}"
    if p.startswith("EK"):
        return "ek", f"Ek {clean_no}"
    if "MÜK" in p or "MUK" in p:
        return "asil", f"Mükerrer {clean_no}"
    return "asil", clean_no


def _inside_quotes(text: str, pos: int) -> bool:
    """Konumun tırnak içi alıntı madde ('“MADDE 9-...”') olup olmadığını kestirir."""
    prefix = text[max(0, pos - 1200):pos]
    opens = prefix.count("“")
    closes = prefix.count("”")
    if opens > closes:
        return True
    # Düz çift tırnak için eşlik kontrolü
    if prefix.count('"') % 2 == 1:
        return True
    return False


def _split_trailing_heading(chunk: str) -> tuple[str, str]:
    """Önceki madde gövdesinin sonundaki kısa madde başlığını ayırır."""
    s = chunk.rstrip()
    if not s:
        return "", ""
    # Son cümle bitişinden (., ?, !, ”, ), ;) sonraki kısa parça başlıktır.
    m = re.search(r"^(?P<body>.*[\.\?\!\”\)\;])\s+(?P<head>[^\.\?\!\;]{2,90})$", s, re.S)
    if not m:
        return s, ""
    head = m.group("head").strip()
    # Başlık [1] dipnotuyla başlıyorsa veya rakamla/bağlaçla başlıyorsa gövde parçasıdır.
    if head.startswith(("[", "(")) or re.match(r"^(?:\d+|ve|veya|ile|bu|ancak|madde)\b", head, re.I):
        return s, ""
    if len(head.split()) > 12:
        return s, ""
    return m.group("body").rstrip(), head


def _split_fikralar(body: str) -> list[dict]:
    body = body.strip()
    if not body:
        return []

    # Numaralı fıkra başlangıçlarını bul (sıralı veya "(1)" ile başlayanlar).
    matches = list(RE_FIKRA_SPLIT.finditer(body))
    valid_starts: list[tuple[int, int, int]] = []
    if matches:
        expected = 1
        for m in matches:
            n = int(m.group(1))
            if n == expected or (not valid_starts and n == 1):
                # "(1) numaralı bent" gibi referansları dışla.
                after = body[m.end():m.end() + 25].lower()
                if after.startswith(("numaralı", "inci", "ıncı", "üncü", "uncu", "ve ", "ila ")):
                    continue
                paren_pos = body.find(f"({n})", m.start())
                valid_starts.append((paren_pos, m.end(), n))
                expected = n + 1

    if valid_starts:
        out: list[dict] = []
        # İlk "(1)" öncesinde değişiklik notu vs. varsa ilk fıkraya ekle
        prefix = body[:valid_starts[0][0]].strip()
        for idx, (pos, _end, n) in enumerate(valid_starts):
            nxt = valid_starts[idx + 1][0] if idx + 1 < len(valid_starts) else len(body)
            ftext = body[pos:nxt].strip()
            if idx == 0 and prefix:
                ftext = f"{prefix} {ftext}".strip()
            out.append({
                "fikra_no": n,
                "metin": ftext,
                "mulga": bool(re.match(r"^(\(\d+\)\s*)?\([^()]*Mülga[^()]*\)\s*\.?\s*$", ftext, re.I)),
                "numara_kaynagi": "metin",
            })
        return out

    # Numarasız metin: satır sonları varsa paragraf/bent kurallarıyla böl, yoksa tek fıkra.
    raw_paras = [p.strip() for p in re.split(r"\n+", body) if p.strip()]
    if len(raw_paras) <= 1:
        return [{
            "fikra_no": 1,
            "metin": body,
            "mulga": bool(RE_MULGA_FULL.match(body)),
            "numara_kaynagi": "sira",
        }]

    paras: list[str] = []
    for p in raw_paras:
        if not paras:
            paras.append(p)
        else:
            prev = paras[-1].rstrip()
            last_line = prev.split("\n")[-1]
            closes_list = (RE_BENT.match(last_line) and prev[-1:] in ",;") or prev.endswith(("veya", "ve"))
            if RE_BENT.match(p) or prev.endswith((":", ";")) or closes_list:
                paras[-1] += "\n" + p
            else:
                paras.append(p)

    return [{
        "fikra_no": i,
        "metin": p,
        "mulga": bool(RE_MULGA_FULL.match(p)),
        "numara_kaynagi": "sira",
    } for i, p in enumerate(paras, start=1)]


def _extract_tail_footnotes(text: str) -> tuple[str, list[dict]]:
    m = RE_TAIL_FOOTNOTES.search(text)
    if not m:
        return text, []
    tail = text[m.start():].strip()
    if not tail.startswith("[1]"):
        return text, []
    notes: list[dict] = []
    parts = re.split(r"(?:^|\s+)\[(\d+)\]\s+", tail)
    # parts: ['', '1', 'metin1', '2', 'metin2', ...]
    for i in range(1, len(parts) - 1, 2):
        notes.append({"no": int(parts[i]), "metin": parts[i + 1].strip()})
    if not notes:
        return text, []
    return text[:m.start()].rstrip(), notes


def parse_law_text(
    text: str,
    law_no: str,
    belge_id: str,
    belge_adi: str | None = None,
) -> list[Article]:
    """Tek bir kanun metnini Article listesine ayrıştırır."""
    clean_text = re.sub(r"[ \t\u00a0]+", " ", text).strip()
    extracted_adi, body = _extract_title_and_body(clean_text, law_no)
    adi = belge_adi or extracted_adi
    kisa = f"{law_no} s. {adi}" if len(adi) <= 55 else f"{law_no} s. {adi[:52].rstrip()}..."

    matches = [m for m in RE_MADDE.finditer(body) if not _inside_quotes(body, m.start())]
    if not matches:
        return []

    # İlk maddeden sonra gelen ek/değişiklik cetveli sınırını kes.
    first_pos = matches[0].start()
    end_m = RE_END_MARKERS.search(body, first_pos)
    if end_m:
        body = body[:end_m.start()].rstrip()
        matches = [m for m in matches if m.start() < end_m.start()]

    if not matches:
        return []

    articles: list[Article] = []
    bolum = ""
    pending_baslik = ""
    preamble = body[:matches[0].start()].strip()
    if preamble:
        bm = RE_BOLUM_HEADER.search(preamble)
        if bm:
            bolum = _norm(bm.group(1))
            rest = preamble[bm.end():].strip(" .")
            if rest:
                if len(rest) <= 90 and not re.search(r"[\.\?\!\;]", rest):
                    pending_baslik = rest
                else:
                    _, pending_baslik = _split_trailing_heading(rest)
        elif len(preamble) <= 90 and not re.search(r"[\.\?\!\;]", preamble):
            pending_baslik = preamble
        else:
            _, pending_baslik = _split_trailing_heading(preamble)

    for i, m in enumerate(matches):
        seg_start = m.end()
        seg_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        raw_seg = RE_LEADING_SEP.sub("", body[seg_start:seg_end]).strip()

        dipnotlar: list[dict] = []
        if i + 1 == len(matches):
            raw_seg, dipnotlar = _extract_tail_footnotes(raw_seg)

        next_baslik = ""
        if i + 1 < len(matches):
            raw_seg, next_baslik = _split_trailing_heading(raw_seg)

        tur, madde_no = _madde_tur_ve_no(m.group("tur"), m.group("no"))
        whole = raw_seg.strip()
        annots = [a.strip() for a in RE_ANNOT.findall(whole)]
        mulga = bool(RE_MULGA_FULL.match(whole))
        islendi = bool(RE_ISLENDI.match(whole))

        fikralar = _split_fikralar(whole)
        articles.append(Article(
            belge_id=belge_id,
            belge_tur="kanun",
            belge_no=str(law_no),
            belge_adi=adi,
            kisa_ad=kisa,
            madde_tur=tur,
            madde_no=madde_no,
            baslik=pending_baslik,
            bolum=bolum,
            sayfa=None,
            mulga=mulga,
            diger_kanuna_islendi=islendi,
            degisiklik_notlari=annots,
            fikralar=fikralar,
            dipnotlar=dipnotlar,
        ))
        pending_baslik = next_baslik

    return articles


def _eksik_asil_numaralar(articles: list[Article]) -> list[int]:
    asil_nos = sorted({
        int(a.madde_no)
        for a in articles
        if a.madde_tur == "asil" and a.madde_no.isdigit()
    })
    if len(asil_nos) < 2:
        return []
    expected = set(range(asil_nos[0], asil_nos[-1] + 1))
    return sorted(expected - set(asil_nos))


def parse_all(
    hf_dir: Path = HF_DIR,
    out_path: Path = OUT_PATH,
    report_path: Path = REPORT_PATH,
    seed: int = 7,
) -> dict:
    """hf_corpus JSON dosyalarını ayrıştırır, JSONL ve kalite raporu üretir."""
    files = sorted(Path(hf_dir).glob("*.json"))
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    law_stats: list[dict] = []
    skipped_deep: list[str] = []
    no_articles: list[str] = []
    all_articles_by_law: dict[str, list[Article]] = {}
    total_articles = 0

    with out_path.open("w", encoding="utf-8") as fh:
        for f in files:
            data = json.loads(f.read_text(encoding="utf-8"))
            law_no = str(data.get("law_number") or "").strip()
            if law_no in SKIP_LAWS:
                skipped_deep.append(law_no)
                continue

            belge_id = _belge_id_from_path(f, law_no)
            arts = parse_law_text(data.get("text") or "", law_no, belge_id)
            if not arts:
                no_articles.append(f"{belge_id} ({f.name})")
                continue

            for a in arts:
                fh.write(json.dumps(asdict(a), ensure_ascii=False) + "\n")
            total_articles += len(arts)
            all_articles_by_law[belge_id] = arts

            missing = _eksik_asil_numaralar(arts)
            law_stats.append({
                "belge_id": belge_id,
                "belge_no": law_no,
                "belge_adi": arts[0].belge_adi,
                "madde_sayisi": len(arts),
                "eksik_sayilar": missing,
            })

    top5 = sorted(law_stats, key=lambda x: x["madde_sayisi"], reverse=True)[:5]
    with_gaps = [x for x in law_stats if x["eksik_sayilar"]]

    rng = random.Random(seed)
    sample_ids = rng.sample(sorted(all_articles_by_law.keys()), min(5, len(all_articles_by_law)))

    lines = [
        "# Geniş Katman Ayrıştırma Raporu (HF Corpus)",
        "",
        f"- Toplam dosya: **{len(files)}**",
        f"- Derin katman olduğu için atlananlar ({len(skipped_deep)}): {', '.join(sorted(skipped_deep)) or 'yok'}",
        f"- Ayrıştırılan kanun sayısı: **{len(law_stats)}**",
        f"- Toplam madde sayısı: **{total_articles}**",
        f"- Madde bulunamayan kanunlar ({len(no_articles)}): {', '.join(no_articles) if no_articles else 'yok'}",
        f"- Asıl madde numarasında atlama olan kanun sayısı: **{len(with_gaps)}**",
        "",
        "## En Çok Maddeli 5 Kanun",
        "| Sıra | Belge ID | Kanun Adı | Madde Sayısı |",
        "|---|---|---|---|",
    ]
    for idx, x in enumerate(top5, start=1):
        lines.append(f"| {idx} | `{x['belge_id']}` | {x['belge_adi']} | {x['madde_sayisi']} |")

    lines.extend([
        "",
        "## Numara Atlaması Olan Kanunlar (İlk 10 Örnek)",
        "| Belge ID | Kanun Adı | Madde | Eksik Numaralar (ilk 10) |",
        "|---|---|---|---|",
    ])
    for x in with_gaps[:10]:
        ex = ", ".join(str(n) for n in x["eksik_sayilar"][:10])
        if len(x["eksik_sayilar"]) > 10:
            ex += f" ... (+{len(x['eksik_sayilar']) - 10})"
        lines.append(f"| `{x['belge_id']}` | {x['belge_adi']} | {x['madde_sayisi']} | {ex} |")

    lines.extend(["", f"## Rastgele 5 Kanundan İlk 3 Madde (seed={seed})"])
    for bid in sample_ids:
        arts = all_articles_by_law[bid]
        lines.append(f"\n### `{bid}` — {arts[0].belge_adi} ({len(arts)} madde)")
        for a in arts[:3]:
            preview = " ".join(f["metin"] for f in a.fikralar)[:220].replace("\n", " ")
            lines.append(
                f"- **Madde {a.madde_no}** (`{a.madde_tur}`, fıkra={len(a.fikralar)}, "
                f"mulga={a.mulga}, baslik={a.baslik!r}): {preview}..."
            )

    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "toplam_dosya": len(files),
        "atlanan_derin": sorted(skipped_deep),
        "kanun_sayisi": len(law_stats),
        "toplam_madde": total_articles,
        "madde_bulunamayan": no_articles,
        "numara_atlamali_kanun": len(with_gaps),
        "out_path": str(out_path),
        "report_path": str(report_path),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="HF corpus kanunlarını Article JSONL'e ayrıştırır")
    ap.add_argument("--hf-dir", default=str(HF_DIR))
    ap.add_argument("--out", default=str(OUT_PATH))
    ap.add_argument("--rapor", default=str(REPORT_PATH))
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    res = parse_all(Path(args.hf_dir), Path(args.out), Path(args.rapor), seed=args.seed)
    print(
        f"Tamamlandı: {res['kanun_sayisi']} kanun, {res['toplam_madde']} madde, "
        f"atlanan derin={res['atlanan_derin']}, madde bulunamayan={len(res['madde_bulunamayan'])}, "
        f"numara atlamalı={res['numara_atlamali_kanun']} -> {res['out_path']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
