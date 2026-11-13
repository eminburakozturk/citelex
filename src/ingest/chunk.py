"""articles.jsonl -> chunks.jsonl (arama/indeks birimi).

Modlar (15 Kas karşılaştırması için parametrik):
  madde  : her madde tek parça
  fikra  : her fıkra ayrı parça
  hibrit : madde <= max_chars ise tek parça, değilse fıkra fıkra (varsayılan, PLAN.md)
  fikra/hibrit modlarında 3000 karakteri aşan bent listeleri ayrıca parçalanır (split_long).

Mülga ve başka kanuna işlenmiş hükümler ATILMAZ, bayrakla yazılır; indeks/arama katmanı
varsayılan olarak bunları filtreler (ör. "X maddesi yürürlükte mi?" sorusu için lazım olabilir).

Kullanım: python -m src.ingest.chunk --mode hibrit --max-chars 1500
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from src.ingest.parse import RE_BENT

SPLIT_CHARS = 3000   # bundan uzun fıkra/madde bent gruplarına bölünür (arama bağlamındaki MAX_MADDE_CHARS ile aynı)
PART_CHARS = 1500    # hedef parça boyu (giriş ve kapanış hariç)
RE_GRUP = re.compile(r"^[IVX]+\s*[-–]\s")

def atif(a: dict, fikra_no: int | None) -> str:
    """Kanun: '6698 s. KVKK m. 5/2'. Yönetmelik/tebliğ: 'Yıllık Ücretli İzin Yön. m. 9'."""
    tur = {"asil": "m.", "ek": "ek m.", "gecici": "geç. m."}[a["madde_tur"]]
    no = a["madde_no"].split()[-1]
    ad = a["kisa_ad"]
    if a["belge_tur"] == "kanun" and not ad.startswith(a["belge_no"]):
        ad = f"{a['belge_no']} s. {ad}"
    return f"{ad} {tur} {no}" + (f"/{fikra_no}" if fikra_no is not None else "")


def header(a: dict, fikra_no: int | None) -> str:
    h = f"{a['belge_no']} sayılı {a['belge_adi']}, " if a["belge_tur"] == "kanun" else f"{a['belge_adi']}, "
    h += {"asil": "Madde", "ek": "Ek Madde", "gecici": "Geçici Madde"}[a["madde_tur"]]
    h += f" {a['madde_no'].split()[-1]}"
    if a["baslik"]:
        h += f" ({a['baslik']})"
    if fikra_no is not None:
        h += f", fıkra {fikra_no}"
    return h


def split_long(metin: str) -> list[tuple[str, str]] | None:
    """Çok uzun bent listesini (tanımlar, ceza bentleri) parçalara böl: [(giriş, parça metni)] veya None.

    Gerekçe (ölçüldü, 6331 eklenince): 5.000 karakterlik "Tanımlar" fıkrası her terimi içerdiği için ilgisiz
    sorularda üst sıraya çıkıyor ve bağlam bütçesini tek başına tüketip asıl maddeyi dışarı itiyordu.
    Her parça giriş cümlesini ("Bu Kanunun uygulanmasında;"), varsa ait olduğu "II- ..." grup başlığını ve
    listeyi kapatan kısa cümleyi ("ifade eder.", "idari para cezası verilir.") taşır; tek başına okunabilir.
    """
    lines = metin.split("\n")
    if len(metin) <= SPLIT_CHARS or len(lines) < 4:
        return None
    giris, govde = lines[0], lines[1:]
    kapanis = ""
    if len(govde[-1]) < 200 and not RE_BENT.match(govde[-1]):
        kapanis, govde = govde[-1], govde[:-1]
    parts: list[tuple[str, list[str]]] = []
    cur: list[str] = []
    grup = cur_grup = None

    def flush() -> None:
        if cur:
            parts.append((giris + (f"\n{cur_grup}" if cur_grup else ""), list(cur)))
            cur.clear()

    for ln in govde:
        if RE_GRUP.match(ln):          # "II- Ahlak ve iyi niyet kurallarına uymayan haller": yeni grup, yeni parça
            flush()
            grup, cur_grup = ln, None  # başlık parçanın ilk satırı; girişte tekrarlanmaz
        elif cur and sum(len(x) + 1 for x in cur) + len(ln) > PART_CHARS:
            flush()
            cur_grup = grup
        cur.append(ln)
    flush()
    if len(parts) < 2:
        return None
    return [(g, "\n".join([g, *body] + ([kapanis] if kapanis else []))) for g, body in parts]


def make_chunk(a: dict, fikralar: list[dict], fikra_no: int | None, parca: tuple[int, str, str] | None = None) -> dict:
    metin = parca[2] if parca else "\n".join(f["metin"] for f in fikralar)
    mid = f"{a['belge_id']}-{a['madde_tur']}-{a['madde_no'].split()[-1]}"
    return {
        "chunk_id": mid + (f"-f{fikra_no}" if fikra_no is not None else "") + (f"-p{parca[0]}" if parca else ""),
        "parca_no": parca[0] if parca else None,   # uzun fıkranın kaçıncı parçası (split_long)
        "giris": parca[1] if parca else None,      # her parçada tekrarlanan giriş (gösterimde ayıklamak için)
        "belge_id": a["belge_id"],
        "belge_tur": a["belge_tur"],
        "belge_no": a["belge_no"],
        "belge_adi": a["belge_adi"],
        "madde_tur": a["madde_tur"],
        "madde_no": a["madde_no"],
        "fikra_no": fikra_no,
        "fikra_numara_kaynagi": fikralar[0].get("numara_kaynagi") if fikra_no is not None else None,
        "baslik": a["baslik"],
        "bolum": a["bolum"],
        "sayfa": a["sayfa"],
        "atif": atif(a, fikra_no),
        "mulga": a["mulga"] or all(f["mulga"] for f in fikralar),
        "diger_kanuna_islendi": a["diger_kanuna_islendi"],
        "dipnotlar": a["dipnotlar"],   # değişiklik geçmişi; embed_text'e girmez, cevap bağlamına eklenebilir
        "metin": metin,
        "embed_text": header(a, fikra_no) + "\n" + metin,
    }


def chunk_article(a: dict, mode: str, max_chars: int) -> list[dict]:
    fk = a["fikralar"]
    total = sum(len(f["metin"]) for f in fk)
    if mode == "madde":
        return [make_chunk(a, fk, None)]
    units = [(fk, None)] if mode == "hibrit" and (total <= max_chars or len(fk) == 1) else [([f], f["fikra_no"]) for f in fk]
    out = []
    for fs, no in units:
        parts = None if a["mulga"] or all(f["mulga"] for f in fs) else split_long("\n".join(f["metin"] for f in fs))
        if parts:
            out += [make_chunk(a, fs, no, (i, g, m)) for i, (g, m) in enumerate(parts, 1)]
        else:
            out.append(make_chunk(a, fs, no))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["madde", "fikra", "hibrit"], default="hibrit")
    ap.add_argument("--max-chars", type=int, default=1500)
    ap.add_argument("--src", default="data/processed/articles.jsonl")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    out = Path(args.out or f"data/processed/chunks_{args.mode}.jsonl")
    arts = [json.loads(l) for l in open(args.src, encoding="utf-8")]
    chunks = [c for a in arts for c in chunk_article(a, args.mode, args.max_chars)]
    ids = [c["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids)), "tekrarlanan chunk_id"
    with out.open("w", encoding="utf-8") as fh:
        for c in chunks:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    aktif = [c for c in chunks if not (c["mulga"] or c["diger_kanuna_islendi"])]
    print(f"{len(chunks)} parça ({len(aktif)} aktif) -> {out}")


if __name__ == "__main__":
    main()
