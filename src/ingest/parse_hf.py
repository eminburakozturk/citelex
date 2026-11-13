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
RE_FIKRA_SPLIT = re.compile(r"(?:^|(?<=[\.\)\”\"\]])\s+)\((\d+)\)\s+(?=[A-ZÇĞİÖŞÜa-zçğıöşü0-9\(\“\"])")
RE_BENT = re.compile(r"^([a-zçğıöşüа]{1,2}\)|\([IVX]+\)|[IVX]+\s*[-–.]\s|\([a-zçğıöşü]\)\s|\d+\.\s|\d+\)\s|[A-Z]\s*[-–]\s|[a-zçğıöşü]\.\s)")
RE_ANNOT = re.compile(r"\((?:[^()]*?)(?:Ek|Değişik|Mülga|İptal|Başlığı|Yeniden)[^()]*?\)")
RE_MULGA_FULL = re.compile(r"^(?:\([^)]*Mülga[^)]*\)|Mülga\s*:[^.]*)\s*\.?\s*$", re.I)
RE_ISLENDI = re.compile(r"^\(?.*ilgili olup.*yer(?:ler)?ine işlenmiştir\.?\)?\s*$", re.S | re.I)

# Künye blokları: Yayımlandığı Resmî Gazete ve/veya Yayımlandığı Düstur (farklı sıralarda ve eksik alanlarla gelebilir)
_RE_RG_BLOCK = r"Yayımlan?dığı\s+Resm[îi]\s+Gazete\s*:.*?\bSayı\s*:\s*[\d/\-]+(?:\s*\([^)]*\))?(?:\s+Mükerrer)?"
_RE_DUSTUR_BLOCK = (
    r"Yayımlan?dığı\s+Düstur\s*:\s*"
    r"(?:Tertip\s*:\s*[\d\-]*\s*)?"
    r"(?:Cilt\s*:\s*[\d/\-]*\s*)?"
    r"(?:Sayfa\s*:\s*[\d/\-]*\s*)?"
)
RE_KUNYE_HEAD = re.compile(
    r"^(?P<adi>.+?)\s+(?:Kanun(?:un|u)?|Kabul)?\s*(?:Numarası|Maddesi)\s*:\s*\d+(?:/\d+)?\s+"
    rf"(?:Kabul\s+Tarih[i]?\s*:\s*[\d/.\-]+(?:\s+ve\s+[\d/.\-]+)?\s*)?"
    rf"(?:(?:{_RE_RG_BLOCK}|{_RE_DUSTUR_BLOCK})\s*)+",
    re.I,
)
RE_KUNYE_TAIL_CLEAN = re.compile(
    rf"(?:^|\s+)(?:{_RE_DUSTUR_BLOCK}|{_RE_RG_BLOCK})\s*",
    re.I,
)

# Mevzuat.gov.tr değişiklik/ek cetveli (kanunun kendi ek listelerinden sonra veya sonunda yer alır)
RE_END_MARKERS = re.compile(
    r"(?:1\s+SAYILI\s+LİSTE\s+)?\bEK\s+MADDE\s+EKLEYEN\s+VEYA\s+MÜSTAKİL\s+HÜKÜM\s+GETİREN\s+KANUN\b|"
    r"\b\d+\s+SAYILI\s+KANUNA\s+EK\s+VE\s+DEĞİŞİKLİK\b|"
    r"\b(?:ANA\s+)?KANUNA\s+İŞLENEMEYEN\s+HÜKÜMLER\b|"
    r"\bİŞLENEMEYEN\s+HÜKÜMLER\b",
    re.I,
)

_ORDINALS = (
    r"(?:[A-ZÇĞİÖŞÜliI]{4,14}(?:NC[Iİ]|NC[UÜ])|"
    r"BİRİNCİ|İKİNCİ|ÜÇÜNCÜ|DÖRDÜNCÜ|BEŞİNCİ|ALTINCI|YEDİNCİ|SEKİZİNCİ|DOKUZUNCU|ONUNCU|"
    r"ONBİRİNCİ|ONİKİNCİ|ONÜÇÜNCÜ|ONDÖRDÜNCÜ|ONBEŞİNCİ|ONALTINCI|ONYEDİNCİ|ONSEKİZİNCİ|"
    r"ONDOKUZUNCU|YİRMİNCİ)"
)
_SEC_KEYWORDS = r"(?:KISIM|BÖLÜM|FASIL|KİTAP|BAP|BAB)"
RE_SECTION_START = re.compile(
    rf"^(?:(?:{_ORDINALS}|[IVXLCDM]+|\d+)\s+{_SEC_KEYWORDS}|{_SEC_KEYWORDS}\s*[:\-{_DASHES}]?\s*(?:[IVXLCDM]+|\d+)?)\b",
)
RE_ANY_SECTION = re.compile(
    rf"(?:(?:{_ORDINALS}|[IVXLCDM]+|\d+)\s+{_SEC_KEYWORDS}|\b{_SEC_KEYWORDS}(?:\s*[:\-{_DASHES}]?\s*(?:[IVXLCDM]+|\d+))?)\b",
)

RE_TAIL_FOOTNOTES = re.compile(r"(?<=\.)\s+(?=\[1\]\s)")

# Ek liste / cetvel / tarife / tablo / çizelge / EK-1 başlıkları (büyük harf duyarlı ki cümle içi "sayılı liste" atıfları karışmasın)
RE_EK_LISTE_HEADER = re.compile(
    rf"(?:^|(?<=[\.\)\]\;]))\s+"
    rf"(?P<ek_ad>"
    rf"(?:\(\s*[IVXLCDM0-9A-Z]+\s*\)|[IVXLCDM0-9]+(?:\s*(?:nci|ncı|üncü|uncu|inci))?)\s+SAYILI\s+(?:LİSTE|CETVEL|TARİFE|TABLO|ÇİZELGE)|"
    rf"EK\s*[{_DASHES}]\s*(?:[IVXLCDM0-9]+|[A-Z])(?:\s+SAYILI\s+(?:LİSTE|CETVEL|TARİFE|TABLO|ÇİZELGE))?|"
    rf"EK\s+(?:LİSTE|CETVEL|TARİFE|TABLO|ÇİZELGE)|"
    rf"(?:LİSTE|CETVEL|TARİFE)(?=\s+(?:Sıra|No|\d+|I\s*[.\-{_DASHES}]))"
    rf")"
    rf"(?!\s*[-–]?(?:n[iıuü]n|n[ea]|nd[ea]|d[ea]n|y[il]?[ea]|s[iı]))"
    rf"(?=\s|\[|$)",
)
# Aynı zamanda cümle başında "(Ek: ...)" notu hemen öncesinde gelebilir: "(Ek: 30/4/2014-6537/5 md.) (1) SAYILI LİSTE"
RE_EK_LEADING_ANNOT = re.compile(r"\(\s*(?:Ek|Değişik|Yeniden)\s*:[^()]+\)\s*$")


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
    head_slice = text[:1800]
    m = RE_KUNYE_HEAD.match(head_slice)
    if m:
        adi = re.sub(r"\s*\[\d+\]\s*", " ", m.group("adi")).strip(" -–—:")
        rest = RE_KUNYE_TAIL_CLEAN.sub(" ", text[m.end():]).strip() if m.end() < 1600 else text[m.end():].strip()
        # Eğer hemen başında tarih/sayı artığı kaldıysa (ör. 213 sayılı Kanundaki çifte RG tarihleri) ilk madde/bölüme kadar temizle
        rest = re.sub(r"^(?:[\d/.\-]+\s+){1,6}(?=Yayımlan|GİRİŞ|" + _ORDINALS + r"|[A-ZÇĞİÖŞÜ])", "", rest).strip()
        rest = RE_KUNYE_TAIL_CLEAN.sub("", rest).strip()
        return _norm(adi) or f"{law_no} Sayılı Kanun", rest

    m_no = re.search(r"^(?P<adi>.+?)\s+(?:Kanun(?:un|u)?|Kabul)?\s*(?:Numarası|Maddesi)\s*:", head_slice, re.I)
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
    if prefix.count('"') % 2 == 1:
        return True
    return False


def _clean_baslik_text(s: str) -> str:
    s = RE_KUNYE_TAIL_CLEAN.sub(" ", s)
    s = re.sub(r"\b(?:Tertip\s*:\s*[\d\-]*|Cilt\s*:\s*[\d/\-]*|Sayfa\s*:\s*[\d/\-]*)\s*", "", s, flags=re.I)
    s = re.sub(r"^\s*\[\d+\]\s*", "", s)
    return _norm(s).strip(" .")


def _extract_bolum_and_baslik(head: str, cur_bolum: str) -> tuple[str, str]:
    """Başlık adayını bölüm (KISIM/BÖLÜM/FASIL) ve madde başlığı olarak ayırır."""
    cleaned = _clean_baslik_text(head)
    if not cleaned:
        return cur_bolum, ""

    sec_matches = list(RE_ANY_SECTION.finditer(cleaned))
    if not sec_matches:
        return cur_bolum, cleaned

    last_m = sec_matches[-1]
    after = cleaned[last_m.end():].strip(" .")
    # Bölüm adı ile madde başlığı arasında ".", ":" veya dipnot "[n]" varsa ayır
    # Örn: "BİRİNCİ BÖLÜM Genel Hükümler. Amaç ve kapsam" -> bolum="BİRİNCİ BÖLÜM Genel Hükümler", baslik="Amaç ve kapsam"
    if "." in after:
        sec_title, _, rest_title = after.partition(".")
        new_bolum = _norm(cleaned[:last_m.end()] + " " + sec_title)
        return new_bolum, _clean_baslik_text(rest_title)

    # Eğer başlıkta iki nokta ile biten veya ":" öncesi kısa bölüm adı ayrımı varsa (örn: "... Kabul Avukatlığa kabul şartları:")
    # Bölüm adından sonra son kısa cümle/ifade varsa yalnız net ayraçlı (dipnot [n] sonrası veya ":" sonrası değil öncesi) ayır
    m_fn = re.search(r"\[\d+\]\s+(.+)$", after)
    if m_fn:
        sec_part = after[:m_fn.start()].strip()
        new_bolum = _norm(cleaned[:last_m.end()] + " " + sec_part)
        return new_bolum, _clean_baslik_text(m_fn.group(1))

    # Bölüm başlığından sonraki 2-4 kelimelik büyük-küçük harfli bölüm adını bolum yap, madde başlığı belirsizse boş bırak
    words = after.split()
    if len(words) >= 5 and after.endswith(":"):
        # Tipik: "<Bölüm Adı (2-3 TitleCase kelime)> <Madde başlığı:>"
        split_idx = 2
        for idx in range(1, min(4, len(words) - 1)):
            if words[idx][0].islower():
                split_idx = idx - 1
                break
            split_idx = idx + 1
        split_idx = max(1, min(split_idx, len(words) - 2))
        new_bolum = _norm(cleaned[:last_m.end()] + " " + " ".join(words[:split_idx]))
        return new_bolum, _clean_baslik_text(" ".join(words[split_idx:]))

    return _norm(cleaned), ""


def _split_trailing_heading(chunk: str, cur_bolum: str) -> tuple[str, str, str]:
    """Önceki madde gövdesinin sonundaki bölüm ve/veya kısa madde başlığını ayırır."""
    s = chunk.rstrip()
    if not s:
        return "", cur_bolum, ""
    m = re.search(
        r"^(?P<body>.*(?:[\.\?\!\”\;]|(?<!\s[A-ZÇĞİÖŞÜ])(?<!\s[IVX]{2})(?<!\s[IVX]{3})\)))\s+(?P<head>[^\.\?\!\;]{2,140})$",
        s,
        re.S,
    )
    if not m:
        return s, cur_bolum, ""
    head = m.group("head").strip()
    has_section = bool(RE_ANY_SECTION.search(head))
    if not has_section:
        if len(head) > 90 or len(head.split()) > 12:
            return s, cur_bolum, ""
        if head.startswith(("[", "(")) or re.match(r"^(?:\d+|ve|veya|ile|bu|ancak|madde)\b", head, re.I):
            return s, cur_bolum, ""
    new_bolum, baslik = _extract_bolum_and_baslik(head, cur_bolum)
    return m.group("body").rstrip(), new_bolum, baslik


def _split_sentences_into_chunks(text: str, target_chars: int = 1350) -> list[str]:
    """Uzun düz metni cümle / noktalı virgül sınırlarından ~target_chars parçalara böler."""
    s = _norm(text)
    if len(s) <= target_chars:
        return [s] if s else []

    # Cümle sonları: '.', ';', '?' ardından boşluk (kısaltma "md.", "vd.", "vb.", "No." ve "1." hariç)
    parts = re.split(r"(?<=[;])\s+|(?<!\bmd)(?<!\bvd)(?<!\bvb)(?<!\bNo)(?<!\d)(?<=[\.\?\!])\s+", s)
    chunks: list[str] = []
    cur = ""
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if len(p) > target_chars:
            if cur:
                chunks.append(cur)
                cur = ""
            # Hâlâ uzunsa virgül / boşluk sınırından böl
            words = p.split(" ")
            sub = ""
            for w in words:
                cand = f"{sub} {w}".strip() if sub else w
                if len(cand) <= target_chars:
                    sub = cand
                else:
                    if sub:
                        chunks.append(sub)
                    sub = w
            if sub:
                chunks.append(sub)
            continue

        cand = f"{cur} {p}".strip() if cur else p
        if len(cand) <= target_chars:
            cur = cand
        else:
            if cur:
                chunks.append(cur)
            cur = p
    if cur:
        chunks.append(cur)
    return chunks


def _insert_bent_newlines(text: str) -> str:
    """3000 karakterden uzun bent listelerinde chunk.split_long'un çalışması için bent başlarına \\n koyar."""
    if "\n" in text and len(text.splitlines()) >= 4:
        return text
    # Örn: ": a) ...", "; b) ...", ". 1) ...", "; A - 1) ...", "Madde/bent olmayan tanımlar: Terim: Açıklama"
    formatted = re.sub(
        r"(?<=[:;\.\)\]])\s+(?=(?:[a-zçğıöşüа]{1,2}\)|\(\s*[IVX]+\s*\)|[A-Z]\s*[-–]\s*\d+\)|\d+\)|\d+\.\s+[A-ZÇĞİÖŞÜ“\"]))",
        "\n",
        text,
    )
    # Sözlük/tanım biçimi: "Bakan: ... Müsteşarlık: ..." (en az 4 "Kelime: " kalıbı varsa)
    if formatted.count("\n") < 3:
        cand = re.sub(
            r"(?<=[\.\,;:])\s+(?=[A-ZÇĞİÖŞÜ][A-Za-zçğıöşüÇĞİÖŞÜ0-9 /\-]{1,40}\s*:)",
            "\n",
            text,
        )
        if cand.count("\n") >= 3:
            formatted = cand

    lines = formatted.split("\n")
    if len(lines) >= 4 and len(lines[0]) <= 350 and all(len(ln) <= 2200 for ln in lines):
        return formatted

    # Eğer tek bir bent/satır > 2200 ise veya başlangıç satırı uzun/düz metinse:
    # chunk.split_long lines[0]'ı giriş olarak her parçaya eklediği için lines[0]'ı <= 250 karakter tut.
    out_lines: list[str] = []
    for idx, ln in enumerate(lines):
        if idx == 0 and len(ln) > 250:
            sub = _split_sentences_into_chunks(ln, target_chars=220)
            if sub:
                out_lines.append(sub[0])
                rest = " ".join(sub[1:])
                if rest:
                    out_lines.extend(_split_sentences_into_chunks(rest, target_chars=1150))
            else:
                out_lines.append(ln)
        elif len(ln) > 1400:
            out_lines.extend(_split_sentences_into_chunks(ln, target_chars=1150))
        else:
            out_lines.append(ln)
    return "\n".join(out_lines)


def _split_fikralar(body: str) -> list[dict]:
    body = body.strip()
    if not body:
        return []

    matches = list(RE_FIKRA_SPLIT.finditer(body))
    valid_starts: list[tuple[int, int, int]] = []
    if matches:
        expected = 1
        has_missing_first = bool(re.search(r"\b(?:birinci|1\s*inci)\s+fıkra\b", body[:400], re.I))
        for m in matches:
            n = int(m.group(1))
            if n == expected or (not valid_starts and (n == 1 or (has_missing_first and n == 2))):
                after = body[m.end():m.end() + 25].lower()
                if after.startswith(("numaralı", "inci", "ıncı", "üncü", "uncu", "ve ", "ila ")):
                    continue
                paren_pos = body.find(f"({n})", m.start())
                valid_starts.append((paren_pos, m.end(), n))
                expected = n + 1

    if valid_starts:
        out: list[dict] = []
        prefix = body[:valid_starts[0][0]].strip()
        for idx, (pos, _end, n) in enumerate(valid_starts):
            nxt = valid_starts[idx + 1][0] if idx + 1 < len(valid_starts) else len(body)
            ftext = body[pos:nxt].strip()
            if idx == 0 and prefix:
                ftext = f"{prefix} {ftext}".strip()
            if len(ftext) > 2800 and not re.match(r"^(\(\d+\)\s*)?\([^()]*Mülga[^()]*\)\s*\.?\s*$", ftext, re.I):
                ftext = _insert_bent_newlines(ftext)
            out.append({
                "fikra_no": n,
                "metin": ftext,
                "mulga": bool(re.match(r"^(\(\d+\)\s*)?\([^()]*Mülga[^()]*\)\s*\.?\s*$", ftext, re.I)),
                "numara_kaynagi": "metin",
            })
        return out

    # Numarasız metin
    raw_paras = [p.strip() for p in re.split(r"\n+", body) if p.strip()]
    if len(raw_paras) <= 1:
        if len(body) > 2500 and not RE_MULGA_FULL.match(body):
            # Çok uzun numarasız madde: bent listesi varsa split_long için \n ekle,
            # ya da düz/uzun paragrafları ~1350 karakterlik ardışık fıkralara böl.
            formatted = _insert_bent_newlines(body)
            lines = formatted.split("\n")
            has_short_intro_list = (
                ":" in lines[0][-3:] or ";" in lines[0][-3:] or "şunlardır" in lines[0].lower() or "aşağıda" in lines[0].lower()
            ) and len(lines[0]) <= 300 and len(lines) >= 4
            if has_short_intro_list:
                return [{
                    "fikra_no": 1,
                    "metin": formatted,
                    "mulga": False,
                    "numara_kaynagi": "sira",
                }]
            parts = _split_sentences_into_chunks(body, target_chars=1350)
            return [{
                "fikra_no": i,
                "metin": p,
                "mulga": False,
                "numara_kaynagi": "sira",
            } for i, p in enumerate(parts, start=1)]
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
        "metin": _insert_bent_newlines(p) if len(p) > 2800 else p,
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
    for i in range(1, len(parts) - 1, 2):
        notes.append({"no": int(parts[i]), "metin": parts[i + 1].strip()})
    if not notes:
        return text, []
    return text[:m.start()].rstrip(), notes


def _format_ek_name(raw: str) -> str:
    s = _norm(raw)
    if re.match(r"^EK\s*[-–‒−]", s, re.I):
        return re.sub(rf"\s*[{_DASHES}]\s*", "-", s.upper())
    tokens = s.split()
    out = []
    for tok in tokens:
        up = tok.upper()
        if up not in {"EK", "SAYILI", "LİSTE", "CETVEL", "TARİFE", "TABLO", "ÇİZELGE"} and re.fullmatch(
            r"\(?[IVXLCDM0-9A-Z]+\)?", up
        ):
            out.append(up)
        else:
            low = tok.replace("İ", "i").replace("I", "ı").lower()
            first = low[0].upper() if low else ""
            if low.startswith("i"):
                first = "İ"
            elif low.startswith("ç"):
                first = "Ç"
            elif low.startswith("ş"):
                first = "Ş"
            elif low.startswith("ğ"):
                first = "Ğ"
            elif low.startswith("ö"):
                first = "Ö"
            elif low.startswith("ü"):
                first = "Ü"
            out.append(first + low[1:])
    return " ".join(out)


def _split_ek_body_chunks(ek_ad: str, body: str, max_len: int = 1480) -> list[dict]:
    """Uzun ek metnini satır/kayıt sınırlarından ~1400-1480 karakterlik parçalara böler."""
    prefix = f"[{ek_ad}] "
    budget = max(400, max_len - len(prefix))
    s = _norm(body)
    if not s:
        return [{"fikra_no": 1, "metin": prefix.strip(), "mulga": False, "numara_kaynagi": "sira"}]
    if len(s) <= budget:
        return [{"fikra_no": 1, "metin": f"{prefix}{s}", "mulga": False, "numara_kaynagi": "sira"}]

    # Kayıt/satır sınırları: "1) ...", "123 ANKARA ...", "166 99911762 ÖZEL ...", "1- Çatalan ...", "297. ERZİNCAN ..."
    rows = re.split(
        r"\s+(?=(?:"
        r"\d{1,4}\s+(?:(?:\d{1,3}(?:-\d{2,4}){1,3}|\d{5,})\s+)?[A-ZÇĞİÖŞÜ]"
        r"|\d{1,4}\s*[-–.]\s+[A-ZÇĞİÖŞÜ]"
        r"|\d{1,4}\)\s+"
        r"|I{1,3}V?[-–.\s]+[A-ZÇĞİÖŞÜ]"
        r"|[a-zçğıöşü]\)\s+"
        r"))|(?<=;)\s+|(?<!\d\.)(?<=\.)\s+",
        s,
    )
    chunks: list[str] = []
    cur = ""
    for r in rows:
        r = r.strip()
        if not r:
            continue
        if len(r) > budget:
            if cur:
                chunks.append(cur)
                cur = ""
            chunks.extend(_split_sentences_into_chunks(r, target_chars=budget))
            continue
        cand = f"{cur} {r}".strip() if cur else r
        if len(cand) <= budget:
            cur = cand
        else:
            if cur:
                chunks.append(cur)
            cur = r
    if cur:
        chunks.append(cur)

    return [{
        "fikra_no": idx,
        "metin": f"{prefix}{c}",
        "mulga": bool(RE_MULGA_FULL.match(c)),
        "numara_kaynagi": "sira",
    } for idx, c in enumerate(chunks, start=1)]


def _extract_ek_listeler(raw_seg: str) -> tuple[str, list[tuple[str, str]]]:
    """Madde sonuna yapışmış ek liste/cetvel/tarife/tablo/EK-N bölümlerini ayırır.

    Döner: (asıl madde gövdesi, [(ek_ad, ek_govdesi), ...])
    """
    matches = [m for m in RE_EK_LISTE_HEADER.finditer(raw_seg) if not _inside_quotes(raw_seg, m.start())]
    if not matches:
        return raw_seg, []

    # Yalnız ilk gerçek ek başlığından öncesinde yürütme/cümle sonu varsa ayır (yanlış pozitif engelleme)
    first = matches[0]
    cut_pos = first.start()
    # Eğer hemen öncesinde "(Ek: 30/4/2014-6537/5 md.)" notu varsa eki onunla başlat
    head_part = raw_seg[:cut_pos].rstrip()
    am = RE_EK_LEADING_ANNOT.search(head_part)
    if am:
        cut_pos = am.start()
        head_part = raw_seg[:cut_pos].rstrip()

    if not head_part:
        return raw_seg, []

    # Cümle/hüküm sonu kontrolü: asıl madde "." / "]" / ")" ile bitmiyorsa ek başlığı cümle ortasıdır -> atla
    if head_part[-1] not in ".])”\"":
        return raw_seg, []

    ekler: list[tuple[str, str]] = []
    for idx, m in enumerate(matches):
        ek_ad = _format_ek_name(m.group("ek_ad"))
        seg_start = m.end()
        seg_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(raw_seg)
        # Sonraki ekin başında (Ek: ...) notu varsa kes
        if idx + 1 < len(matches):
            sub_head = raw_seg[seg_start:seg_end].rstrip()
            sub_am = RE_EK_LEADING_ANNOT.search(sub_head)
            if sub_am:
                seg_end = seg_start + sub_am.start()
        ek_body = RE_LEADING_SEP.sub("", raw_seg[seg_start:seg_end]).strip()
        ekler.append((ek_ad, ek_body))

    return head_part, ekler


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
        preamble_clean = _clean_baslik_text(preamble)
        if preamble_clean:
            if RE_ANY_SECTION.search(preamble_clean):
                bolum, pending_baslik = _extract_bolum_and_baslik(preamble_clean, bolum)
            elif len(preamble_clean) <= 90 and not re.search(r"[\.\?\!\;]", preamble_clean):
                pending_baslik = preamble_clean
            else:
                _, bolum, pending_baslik = _split_trailing_heading(preamble_clean, bolum)

    seen_ek_names: dict[str, int] = {}

    for i, m in enumerate(matches):
        seg_start = m.end()
        seg_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        raw_seg = RE_LEADING_SEP.sub("", body[seg_start:seg_end]).strip()

        dipnotlar: list[dict] = []
        if i + 1 == len(matches):
            raw_seg, dipnotlar = _extract_tail_footnotes(raw_seg)

        # Madde sonuna yapışmış ek listeleri ayır
        raw_seg, ekler = _extract_ek_listeler(raw_seg)

        next_bolum = bolum
        next_baslik = ""
        if i + 1 < len(matches) and not ekler:
            raw_seg, next_bolum, next_baslik = _split_trailing_heading(raw_seg, bolum)

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

        for ek_ad, ek_body in ekler:
            cnt = seen_ek_names.get(ek_ad, 0) + 1
            seen_ek_names[ek_ad] = cnt
            unique_ek_ad = ek_ad if cnt == 1 else f"{ek_ad} ({cnt})"
            ek_annots = [a.strip() for a in RE_ANNOT.findall(ek_body[:400])]
            articles.append(Article(
                belge_id=belge_id,
                belge_tur="kanun",
                belge_no=str(law_no),
                belge_adi=adi,
                kisa_ad=kisa,
                madde_tur="ek_liste",
                madde_no=unique_ek_ad,
                baslik=unique_ek_ad,
                bolum=bolum,
                sayfa=None,
                mulga=bool(RE_MULGA_FULL.match(ek_body)),
                diger_kanuna_islendi=False,
                degisiklik_notlari=ek_annots,
                fikralar=_split_ek_body_chunks(unique_ek_ad, ek_body),
                dipnotlar=[],
            ))

        bolum = next_bolum
        pending_baslik = next_baslik

    # Aynı (madde_tur, madde_no) birden çok kez geçerse ("Geçici Madde 1" vb.) benzersiz yap.
    gor: dict[tuple[str, str], int] = {}
    for a in articles:
        k = (a.madde_tur, a.madde_no)
        gor[k] = gor.get(k, 0) + 1
        if gor[k] > 1:
            a.madde_no = f"{a.madde_no} ({gor[k]})"

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
    total_ek_liste = 0
    total_tekrar_no = 0

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

            # Tekrar numara sayımı (tekilleştirme parse_law_text sonunda yapılır)
            for a in arts:
                if re.search(r" \(\d+\)$", a.madde_no):
                    total_tekrar_no += 1
                fh.write(json.dumps(asdict(a), ensure_ascii=False) + "\n")
                if a.madde_tur == "ek_liste":
                    total_ek_liste += 1
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
        f"- Toplam birim (madde + ek_liste) sayısı: **{total_articles}** (`ek_liste`: **{total_ek_liste}**)",
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
        lines.append(f"\n### `{bid}` — {arts[0].belge_adi} ({len(arts)} birim)")
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
        "ek_liste_sayisi": total_ek_liste,
        "madde_bulunamayan": no_articles,
        "numara_atlamali_kanun": len(with_gaps),
        "out_path": str(out_path),
        "report_path": str(report_path),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="HF mevzuat korpusunu Article JSONL biçimine dönüştür.")
    ap.add_argument("--hf-dir", type=Path, default=HF_DIR)
    ap.add_argument("--out", type=Path, default=OUT_PATH)
    ap.add_argument("--rapor", type=Path, default=REPORT_PATH)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    res = parse_all(args.hf_dir, args.out, args.rapor, args.seed)
    print(
        f"Tamamlandı: {res['kanun_sayisi']} kanun, {res['toplam_madde']} birim "
        f"(ek_liste={res['ek_liste_sayisi']}), atlanan derin={res['atlanan_derin']}, "
        f"madde bulunamayan={len(res['madde_bulunamayan'])}, "
        f"numara atlamalı={res['numara_atlamali_kanun']} -> {res['out_path']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
