"""articles.jsonl -> chunks.jsonl (arama/indeks birimi).

Modlar (15 Kas karşılaştırması için parametrik):
  madde  : her madde tek parça
  fikra  : her fıkra ayrı parça
  hibrit : madde <= max_chars ise tek parça, değilse fıkra fıkra (varsayılan, PLAN.md)

Mülga ve başka kanuna işlenmiş hükümler ATILMAZ, bayrakla yazılır; indeks/arama katmanı
varsayılan olarak bunları filtreler (ör. "X maddesi yürürlükte mi?" sorusu için lazım olabilir).

Kullanım: python -m src.ingest.chunk --mode hibrit --max-chars 1500
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

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


def make_chunk(a: dict, fikralar: list[dict], fikra_no: int | None) -> dict:
    metin = "\n".join(f["metin"] for f in fikralar)
    mid = f"{a['belge_id']}-{a['madde_tur']}-{a['madde_no'].split()[-1]}"
    return {
        "chunk_id": mid + (f"-f{fikra_no}" if fikra_no is not None else ""),
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
    if mode == "madde" or (mode == "hibrit" and (total <= max_chars or len(fk) == 1)):
        return [make_chunk(a, fk, None)]
    return [make_chunk(a, [f], f["fikra_no"]) for f in fk]


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
