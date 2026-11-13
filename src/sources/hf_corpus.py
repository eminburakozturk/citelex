"""Hugging Face hasankursun/turkish-legislation-corpus (CC-BY-4.0) indirici.

Veri kümesini streaming ile okur, her kanunu kanun numarasına göre data/raw/hf_corpus/
altına ayrı JSON dosyası olarak yazar. Yalnız indirir ve kaydeder; ayrıştırma/indeksleme yapmaz.

Kullanım:
  python -m src.sources.hf_corpus --incele --limit 5
  python -m src.sources.hf_corpus --limit 5
  python -m src.sources.hf_corpus
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

from datasets import load_dataset

DATASET_ID = "hasankursun/turkish-legislation-corpus"
OUT_DIR = Path("data/raw/hf_corpus")

_MEVZUAT_NO_RE = re.compile(r"MevzuatNo=(\d+)")
_TERTIP_RE = re.compile(r"MevzuatTertip=(\d+)")


def _resolve_law_info(row: dict) -> tuple[int | None, int | None, bool]:
    """Satırdan (kanun_no, tertip, url_fallback_mi) bilgisini çıkarır."""
    url = row.get("url") or ""
    mt = _TERTIP_RE.search(url)
    tertip = int(mt.group(1)) if mt else None

    raw_no = row.get("law_number")
    if isinstance(raw_no, int) and raw_no > 0:
        return raw_no, tertip, False

    m = _MEVZUAT_NO_RE.search(url)
    if m:
        no = int(m.group(1))
        if no > 0:
            return no, tertip, True
    return None, tertip, False


def _write_law(path: Path, row: dict, law_no: int, tertip: int | None) -> None:
    payload = {
        "law_number": law_no,
        "tertip": tertip,
        "acceptance_date": row.get("acceptance_date"),
        "url": row.get("url"),
        "source": row.get("source"),
        "license": "CC-BY-4.0",
        "text": row.get("text") or "",
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def inspect_corpus(limit: int = 5, split: str = "train") -> list[dict]:
    """Veri kümesinden yalnızca ilk `limit` satırın özetini döndürür."""
    ds = load_dataset(DATASET_ID, split=split, streaming=True)
    out = []
    for idx, row in enumerate(ds):
        if idx >= limit:
            break
        law_no, tertip, from_url = _resolve_law_info(row)
        txt = row.get("text") or ""
        out.append({
            "satir": idx,
            "law_number": law_no,
            "raw_law_number": row.get("law_number"),
            "from_url": from_url,
            "tertip": tertip,
            "acceptance_date": row.get("acceptance_date"),
            "url": row.get("url"),
            "text_len": len(txt),
            "onizleme": txt[:120].replace("\n", " "),
        })
    return out


def indir_ve_kaydet(
    out_dir: Path = OUT_DIR,
    limit: int | None = None,
    split: str = "train",
    dataset_iter: Iterable[dict] | None = None,
) -> dict:
    """HF veri kümesini indirir ve kanun numarasına göre ayrı dosyalara yazar."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = dataset_iter if dataset_iter is not None else load_dataset(DATASET_ID, split=split, streaming=True)
    seen: dict[int, dict] = {}
    atlananlar: list[dict] = []
    toplam = 0
    yazilan = 0
    url_ile_numaralanan = 0
    tertip_ayrisan = 0

    for idx, row in enumerate(rows):
        if limit is not None and idx >= limit:
            break
        toplam += 1
        url = row.get("url") or ""
        txt = row.get("text") or ""
        law_no, tertip, from_url = _resolve_law_info(row)

        if not txt.strip():
            atlananlar.append({"satir": idx, "law_number": law_no, "url": url, "sebep": "bos_metin"})
            continue
        if law_no is None:
            atlananlar.append({"satir": idx, "law_number": None, "url": url, "sebep": "kanun_no_yok"})
            continue
        if from_url:
            url_ile_numaralanan += 1

        if law_no not in seen:
            target = out_dir / f"{law_no}.json"
            _write_law(target, row, law_no, tertip)
            seen[law_no] = {"best_tertip": tertip, "tertips": {tertip}}
            yazilan += 1
            continue

        info = seen[law_no]
        if tertip in info["tertips"]:
            atlananlar.append({
                "satir": idx,
                "law_number": law_no,
                "tertip": tertip,
                "url": url,
                "sebep": "mukerrer",
            })
            continue

        # Farklı Tertip çakışması (ör. 657 Tertip 5 vs Tertip 3): en yeni Tertip ana dosya adını alır.
        tertip_ayrisan += 1
        info["tertips"].add(tertip)
        if (tertip or 0) > (info["best_tertip"] or 0):
            old_tag = info["best_tertip"] if info["best_tertip"] is not None else "x"
            old_primary = out_dir / f"{law_no}.json"
            archived = out_dir / f"{law_no}_t{old_tag}.json"
            if old_primary.exists():
                old_primary.replace(archived)
            _write_law(old_primary, row, law_no, tertip)
            info["best_tertip"] = tertip
        else:
            tag = tertip if tertip is not None else "x"
            _write_law(out_dir / f"{law_no}_t{tag}.json", row, law_no, tertip)
        yazilan += 1

    return {
        "toplam_satir": toplam,
        "yazilan": yazilan,
        "benzersiz_kanun_no": len(seen),
        "url_ile_numaralanan": url_ile_numaralanan,
        "tertip_ayrisan": tertip_ayrisan,
        "atlanan_sayisi": len(atlananlar),
        "atlananlar": atlananlar,
        "out_dir": str(out_dir),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="HF turkish-legislation-corpus indirici")
    ap.add_argument("--limit", type=int, default=None, help="İlk N satırla sınırla")
    ap.add_argument("--out-dir", default=str(OUT_DIR), help="Hedef klasör")
    ap.add_argument("--incele", action="store_true", help="Dosya yazmadan ilk satırları incele")
    args = ap.parse_args()

    try:
        if args.incele:
            items = inspect_corpus(limit=args.limit or 5)
            print(json.dumps(items, ensure_ascii=False, indent=2))
            return 0

        rapor = indir_ve_kaydet(out_dir=Path(args.out_dir), limit=args.limit)
    except Exception as exc:
        print(f"[HATA] Hugging Face veri kümesi alınamadı: {exc}", file=sys.stderr)
        return 1

    print(
        f"Tamamlandı: {rapor['toplam_satir']} satır okundu, "
        f"{rapor['yazilan']} dosya yazıldı ({rapor['benzersiz_kanun_no']} benzersiz kanun no, "
        f"{rapor['url_ile_numaralanan']} URL'den çözülen, {rapor['tertip_ayrisan']} Tertip ayrışan), "
        f"{rapor['atlanan_sayisi']} atlandı -> {rapor['out_dir']}"
    )
    if rapor["atlananlar"]:
        for item in rapor["atlananlar"]:
            print(f"  [ATLANDI] {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
