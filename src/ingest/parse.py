"""mevzuat.gov.tr kanun PDF'lerini madde/fıkra yapısına ayrıştırır.

Neden pdfplumber: mevzuat.gov.tr PDF'leri Word çıktısı. Gövde metni 12 pt, dipnotlar
11 pt italik, dipnot işaretleri 7-8 pt. Karakter boyutuna göre filtrelemek dipnotları
ve metne yapışan dipnot numaralarını ("md.)40" gibi) tek adımda temizler.
Paragraf başı satırlar girintili (x0 ~106 pt), devam satırları sol kenarda (~71 pt).

Kullanım:
    python -m src.ingest.parse data/raw/1.5.6698.pdf data/raw/1.5.4857.pdf
Çıktı: data/processed/articles.jsonl (madde başına bir satır)
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field, asdict
from pathlib import Path

import pdfplumber

# Sayfa düzeni belgeden belgeye değişir (mevzuat.gov.tr Word PDF'i: gövde 12 pt, kenar 71, girinti 106;
# "GeneratePdf" HTML çıktısı: gövde 10.2 pt, kenar 96, girinti 118). Değerler belgeden ölçülür: Layout.
@dataclass
class Layout:
    body_size: float
    margin: float
    indent: float

    @property
    def body_min(self) -> float:          # bundan küçük: dipnot / dipnot işareti
        return self.body_size - 0.5

    @property
    def marker(self) -> tuple[float, float]:   # metin içi dipnot işareti (12 pt gövdede 8 pt)
        return (self.body_size * 0.62, self.body_size * 0.79)

    @property
    def footnote_no_max(self) -> float:   # sayfa altı dipnot numarası (12 pt gövdede 6.5-7 pt)
        return self.body_size * 0.62

    def is_indented(self, x0: float) -> bool:
        return abs(x0 - self.indent) <= 9

    def is_centered(self, x0: float) -> bool:
        return x0 >= self.indent + 40


def measure_layout(pdf) -> Layout:
    sizes: Counter = Counter()
    for page in pdf.pages:
        for c in page.chars:
            if c["text"].strip():
                sizes[round(c["size"], 1)] += 1
    body = sizes.most_common(1)[0][0]
    xs: Counter = Counter()
    for page in pdf.pages:
        b = page.filter(lambda o: o.get("object_type") != "char" or o.get("size", 0) >= body - 0.5)
        for ln in b.extract_text_lines():
            xs[round(ln["x0"])] += 1
    total = sum(xs.values())
    margin = min(x for x, n in xs.items() if n >= 0.05 * total)
    near = {x: n for x, n in xs.items() if margin + 10 <= x <= margin + 50}
    indent = max(near, key=near.get) if near else margin + 35
    return Layout(body, margin, indent)

SOURCES_PATH = Path("configs/sources.json")

RE_MADDE = re.compile(
    r"^(?P<tur>MADDE|Madde|EK MADDE|Ek Madde|Ek madde|GEÇİCİ MADDE|Geçici Madde|Geçici madde)"
    r"\s*(?P<no>\d+)\s*[-–—]?\s*(?P<rest>.*)$"
)
RE_FIKRA_NO = re.compile(r"^\((?P<n>\d+)\)\s*")
RE_BENT = re.compile(r"^([a-zçğıöşü]{1,2}\)|\([IVX]+\)|[IVX]+\s*[-–.]\s|\([a-zçğıöşü]\)\s|\d+\.\s|[a-zçğıöşü]\.\s)")
# Değişiklik notu: "(Değişik: 6/5/2016-6715/1 md.)", "(Ek fıkra:11/6/2003-4884/10 md.)", yönetmeliklerde "(Değişik:RG-28/4/2019-30758)"
RE_ANNOT = re.compile(r"\((?:[^()]*?)(?:Ek|Değişik|Mülga|İptal|Başlığı|Yeniden)[^()]*?\d+/\d+/\d{4}[^()]*?\)")
RE_MULGA_FULL = re.compile(r"^\(\s*Mülga\s*:[^)]*\)\s*$")
RE_ISLENDI = re.compile(r"^\(.*ilgili olup.*yerine işlenmiştir\.?\)\s*$", re.S)
# Kalın yazı tipi adı: "TimesNewRomanPS-BoldMT" veya Türkçe "TimesNewRomanKalın" (PDF'te "Kal?n" bozulabilir)
RE_EK_FORM = re.compile(r"EK\s*[-–]?\s*[IVX0-9]+")   # "EK-I": yönetmelik sonundaki form/cetvel başlığı
RE_BOLD_FONT = re.compile(r"Bold|Kal.{1,2}n", re.I)
END_MARKERS = ("SAYILI CETVEL", "SAYILI KANUNA EK VE DEĞİŞİKLİK", "İŞLENEMEYEN HÜKÜMLER",
               "Yayımlandığı Resmî Gazete")   # sadece ilk madde görüldükten sonra kontrol edilir


@dataclass
class Line:
    text: str
    x0: float
    bold: bool          # satırın ilk kelimesi kalın mı
    all_bold: bool
    page: int
    markers: list[str] = field(default_factory=list)   # satırdaki dipnot işaretleri ("4041" gibi bitişik olabilir)


@dataclass
class Article:
    belge_id: str
    belge_tur: str                  # kanun | yonetmelik | teblig
    belge_no: str
    belge_adi: str
    kisa_ad: str
    madde_tur: str                  # asil | ek | gecici
    madde_no: str                   # "5", "Ek 2", "Geçici 1"
    baslik: str
    bolum: str
    sayfa: int
    mulga: bool = False
    diger_kanuna_islendi: bool = False
    degisiklik_notlari: list[str] = field(default_factory=list)
    fikralar: list[dict] = field(default_factory=list)   # {fikra_no, metin, mulga}
    dipnotlar: list[dict] = field(default_factory=list)  # {no, metin}: değişiklik geçmişi
    _paras: list[str] = field(default_factory=list, repr=False)


def _marker_groups(page, L: Layout) -> list[tuple[float, float, str]]:
    """Metin içindeki dipnot işaretleri: (üst, alt, rakamlar). Bitişik rakamlar tek grup."""
    lo, hi = L.marker
    chars = sorted((c for c in page.chars if lo <= c["size"] < hi and c["text"].strip() and c["text"].isdigit()),
                   key=lambda c: (round(c["top"]), c["x0"]))
    groups: list[list[dict]] = []
    for c in chars:
        if groups and abs(groups[-1][-1]["top"] - c["top"]) < 1 and c["x0"] - groups[-1][-1]["x1"] < 1.5:
            groups[-1].append(c)
        else:
            groups.append([c])
    return [(g[0]["top"], g[0]["bottom"], "".join(c["text"] for c in g)) for g in groups]


def _footnotes(page, L: Layout) -> dict[int, str]:
    """Sayfa altı dipnotlar: küçük numara (12 pt gövdede <7.5 pt) + gövdeden küçük italik metin."""
    FOOTNOTE_NO_MAX = L.footnote_no_max
    fn = page.filter(lambda o: o.get("object_type") != "char" or o.get("size", 12) < FOOTNOTE_NO_MAX
                     or ("Italic" in o.get("fontname", "") and o.get("size", 12) < L.body_min))
    notes: dict[int, str] = {}
    cur = None
    for ln in fn.extract_text_lines(return_chars=True):
        chars = [c for c in ln["chars"] if c["text"].strip()]
        if not chars:
            continue
        lead = ""
        for c in chars:
            if c["size"] < FOOTNOTE_NO_MAX and c["text"].isdigit():
                lead += c["text"]
            else:
                break
        text = re.sub(r"\s+", " ", ln["text"]).strip()
        if lead:
            cur = int(lead)
            notes[cur] = re.sub(r"^\s*" + lead + r"\s*", "", text)
        elif cur is not None:
            notes[cur] += " " + text
    return notes


def read_lines(pdf_path: Path) -> tuple[list[Line], dict[int, str], Layout]:
    out: list[Line] = []
    notes: dict[int, str] = {}
    with pdfplumber.open(pdf_path) as pdf:
        L = measure_layout(pdf)
        for pno, page in enumerate(pdf.pages, start=1):
            groups = _marker_groups(page, L)
            notes.update(_footnotes(page, L))
            body = page.filter(lambda o: o.get("object_type") != "char" or o.get("size", 0) >= L.body_min)
            for ln in body.extract_text_lines(return_chars=True):
                text = re.sub(r"\s+", " ", ln["text"]).strip()
                if not text:
                    continue
                chars = [c for c in ln["chars"] if c["text"].strip()]
                bold_flags = [bool(RE_BOLD_FONT.search(c["fontname"])) for c in chars]
                mk = [g for (top, bottom, g) in groups if ln["top"] - 4 <= top <= ln["bottom"]]
                out.append(Line(text, ln["x0"], bold_flags[0] if bold_flags else False,
                                all(bold_flags) if bold_flags else False, pno, mk))
    return out, notes, L


def split_markers(raw: str, known: set[int], last: int) -> list[int]:
    """Bitişik dipnot işaretlerini çözer: '4041' -> [40, 41], '910' -> [9, 10].

    '23' hem 23 numaralı dipnot hem de 2+3 olabilir; dipnotlar belge sırasıyla
    numaralandığı için, ilk sayısı beklenen sıradaki numara (last+1) olan yorum seçilir.
    Daha önce geçmiş bir numaraya tekrar atıf ("(…)28" iki kez) tek sayı olarak kalır.
    """
    cands: list[list[int]] = []
    if raw.isdigit() and int(raw) in known:
        cands.append([int(raw)])
    for i in range(1, len(raw)):
        start = int(raw[:i])
        seq, n = "", start
        while len(seq) < len(raw):
            seq += str(n)
            n += 1
        if seq == raw and all(k in known for k in range(start, n)):
            cands.append(list(range(start, n)))
    if not cands:
        return []
    for c in cands:
        if c[0] == last + 1:
            return c
    for c in cands:
        if c[-1] <= last:          # tekrar atıf
            return c
    return min(cands, key=lambda c: abs(c[0] - (last + 1)))


def _tur(raw: str) -> str:
    # dikkat: "GEÇİCİ".lower() Python'da birleşik nokta (U+0307) üretir; ilk harfe bak
    first = raw.split()[0][:2].upper()
    return "gecici" if first == "GE" else "ek" if first == "EK" else "asil"


def _madde_label(tur: str, no: str) -> str:
    return {"asil": no, "ek": f"Ek {no}", "gecici": f"Geçici {no}"}[tur]


def load_sources() -> dict:
    data = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def parse(pdf_path: Path, meta: dict) -> list[Article]:
    lines, notes, L = read_lines(pdf_path)
    known = set(notes)
    articles: list[Article] = []
    marker_map: dict[int, list[str]] = {}   # id(article) -> işaretler
    pending_markers: list[str] = []
    cur: Article | None = None
    pending_title: list[str] = []
    bolum, bolum_parts = "", []
    started = False

    def is_indented(ln: Line) -> bool:
        return L.is_indented(ln.x0)

    for ln in lines:
        if started and (any(m in ln.text for m in END_MARKERS) or RE_EK_FORM.fullmatch(ln.text)):
            break   # ek cetvel / form / değişiklik tablosu: madde metni bitti
        m = RE_MADDE.match(ln.text)
        if m and ln.bold and is_indented(ln):
            started = True
            tur = _tur(m["tur"])
            cur = Article(meta["belge_id"], meta["belge_tur"], meta["belge_no"], meta["belge_adi"],
                          meta["kisa_ad"], tur,
                          _madde_label(tur, m["no"]), " ".join(pending_title).strip(),
                          bolum, ln.page)
            pending_title = []
            articles.append(cur)
            marker_map[id(cur)] = pending_markers + ln.markers
            pending_markers = []
            if m["rest"]:
                cur._paras.append(m["rest"])
            continue
        if ln.all_bold and not ln.text.startswith("(") and (is_indented(ln) or L.is_centered(ln.x0)):
            # başlık: ortalanmışsa bölüm başlığı, girintiliyse madde başlığı.
            # Sol kenardaki kalın satırlar (x0~71) başlık değil, kalın gövde metninin devamıdır.
            if L.is_centered(ln.x0):
                if "BÖLÜM" in ln.text or "KISIM" in ln.text:
                    bolum_parts = [ln.text]
                else:
                    bolum_parts.append(ln.text)
                bolum = " - ".join(bolum_parts)
                pending_title = []
            elif started or "BÖLÜM" not in ln.text:
                pending_title.append(ln.text)
                pending_markers.extend(ln.markers)   # başlıktaki işaret sonraki maddeye ait
            continue
        if cur is None:
            continue  # künye / başlık sayfası
        if pending_title:
            # başlık sanılan kalın satır(lar)dan sonra madde başı gelmedi: gövde metnidir
            cur._paras.extend(pending_title)
            pending_title = []
            marker_map[id(cur)].extend(pending_markers)
            pending_markers = []
        marker_map[id(cur)].extend(ln.markers)
        if is_indented(ln) or not cur._paras:
            cur._paras.append(ln.text)
        else:
            cur._paras[-1] += " " + ln.text

    yururlukte = meta.get("yururlukte_maddeler")
    last = 0
    for a in articles:
        _finalize(a)
        nos: list[int] = []
        for raw in marker_map.get(id(a), []):
            res = split_markers(raw, known, last)
            last = max([last] + res)
            for n in res:
                if n not in nos:
                    nos.append(n)
        a.dipnotlar = [{"no": n, "metin": notes[n]} for n in nos]
        if yururlukte is not None and a.madde_no not in yururlukte:
            a.mulga = True
    return articles


def _finalize(a: Article) -> None:
    paras = [p.strip() for p in a._paras if p.strip()]
    whole = " ".join(paras)
    a.degisiklik_notlari = [x.strip() for x in RE_ANNOT.findall(whole)]
    if paras and RE_MULGA_FULL.match(paras[0]) and len(paras) == 1:
        a.mulga = True
    if paras and RE_ISLENDI.match(whole):
        a.diger_kanuna_islendi = True

    # Maddenin tamamını değiştiren not tek başına satırdaysa ("(Değişik: ...)") fıkra değildir
    if paras and not a.mulga and RE_ANNOT.fullmatch(paras[0]):
        paras = paras[1:]

    fikralar: list[str] = []
    explicit = any(RE_FIKRA_NO.match(p) for p in paras)
    for p in paras:
        if not fikralar:
            fikralar.append(p)
        elif explicit:
            # 6698 gibi "(1)", "(2)" numaralı kanunlar: yeni fıkra sadece numarayla başlar
            if RE_FIKRA_NO.match(p):
                fikralar.append(p)
            else:
                fikralar[-1] += "\n" + p
        else:
            # 4857 gibi numarasız kanunlar: girintili paragraf = yeni fıkra, ama
            # bentler ve bent listesini kapatan cümle önceki fıkraya aittir
            prev = fikralar[-1].rstrip()
            last_line = prev.split("\n")[-1]
            closes_list = RE_BENT.match(last_line) and prev[-1:] in ",;" or prev.endswith(("veya", "ve"))
            if RE_BENT.match(p) or prev.endswith((":", ";")) or closes_list:
                fikralar[-1] += "\n" + p
            else:
                fikralar.append(p)

    for i, f in enumerate(fikralar, start=1):
        m = RE_FIKRA_NO.match(f)
        no = int(m["n"]) if m else i
        a.fikralar.append({
            "fikra_no": no,
            "metin": f,
            # "(2) (Mülga: ...)" veya "(Ek fıkra: ...; Mülga dördüncü fıkra: ...)" gibi sadece nottan ibaret fıkra
            "mulga": bool(re.match(r"^(\(\d+\)\s*)?\([^()]*Mülga[^()]*\)\s*$", f)),
            "numara_kaynagi": "metin" if m else "sira",
        })


def main(paths: list[str]) -> None:
    sources = load_sources()
    out = Path("data/processed/articles.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w", encoding="utf-8") as fh:
        for p in paths:
            name = Path(p).name
            if name not in sources:
                print(f"UYARI: {name} configs/sources.json'da yok, atlandı")
                continue
            arts = parse(Path(p), sources[name])
            for a in arts:
                d = asdict(a)
                d.pop("_paras")
                fh.write(json.dumps(d, ensure_ascii=False) + "\n")
            n += len(arts)
            print(f"{p}: {len(arts)} madde")
    print(f"toplam {n} madde -> {out}")


if __name__ == "__main__":
    main(sys.argv[1:] or sorted(str(p) for p in Path("data/raw").glob("*.pdf")))
