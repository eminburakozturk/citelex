"""Geniş katman kalite örneklemi: chunks_genis.jsonl -> results/genis_ornek.md.

Seed=11 ile 40 parça (10 ek_liste, 10 gecici, 20 asil) seçer ve her birinin
data/raw/hf_corpus/*.json içindeki karşılık gelen yerini (±150 karakter)
karşılaştırma tablosu olarak yazar.

Kullanım:
  python -m scripts.genis_ornek
"""
from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

CHUNKS_PATH = Path("data/processed/chunks_genis.jsonl")
HF_DIR = Path("data/raw/hf_corpus")
OUT_PATH = Path("results/genis_ornek.md")


def _hf_path_from_belge_id(hf_dir: Path, belge_id: str) -> Path:
    # "kanun-6749" -> "6749.json", "kanun-657-t3" -> "657_t3.json"
    rest = belge_id.removeprefix("kanun-")
    if "-t" in rest:
        no, tertip = rest.split("-t", 1)
        return hf_dir / f"{no}_t{tertip}.json"
    return hf_dir / f"{rest}.json"


def _clean_anchor_candidates(chunk: dict) -> list[str]:
    metin = chunk["metin"]
    if chunk.get("giris") and metin.startswith(chunk["giris"]):
        tail = metin[len(chunk["giris"]):].strip()
        if tail:
            metin = tail
    # ek_liste ön ekini ("[I Sayılı Liste] ") kaldır
    metin = re.sub(r"^\[[^\]]+\]\s*", "", metin)
    flat = re.sub(r"\s+", " ", metin).strip()
    cands: list[str] = []
    for start in (0, 25, 60, 120):
        if start < len(flat):
            for length in (80, 45, 25):
                sub = flat[start:start + length].strip()
                if len(sub) >= 18:
                    cands.append(sub)
    return cands


def _find_raw_window(raw_text: str, chunk: dict) -> str:
    flat_raw = re.sub(r"\s+", " ", raw_text).strip()
    for cand in _clean_anchor_candidates(chunk):
        idx = flat_raw.find(cand)
        if idx >= 0:
            lo = max(0, idx - 150)
            hi = min(len(flat_raw), idx + len(cand) + 150)
            prefix = "…" if lo > 0 else ""
            suffix = "…" if hi < len(flat_raw) else ""
            return f"{prefix}{flat_raw[lo:hi]}{suffix}"
    # Yedek: ilk anlamlı 3 kelime grubunu case-insensitive ara
    flat_chunk = re.sub(r"^\[[^\]]+\]\s*", "", re.sub(r"\s+", " ", chunk["metin"])).strip()
    words = [w for w in flat_chunk.split() if len(w) >= 4][:4]
    if words:
        m = re.search(re.escape(" ".join(words[:3])), flat_raw, re.I)
        if m:
            lo = max(0, m.start() - 150)
            hi = min(len(flat_raw), m.end() + 150)
            return f"…{flat_raw[lo:hi]}…"
    return "(ham metinde konum eşleştirilemedi)"


def _md_escape(s: str) -> str:
    return s.replace("\n", " ↵ ").replace("|", "\\|")


def sample_chunks(chunks_path: Path = CHUNKS_PATH, seed: int = 11) -> list[dict]:
    chunks = [json.loads(line) for line in Path(chunks_path).read_text(encoding="utf-8").splitlines() if line.strip()]
    ek_pool = [c for c in chunks if c["madde_tur"] == "ek_liste"]
    gecici_pool = [c for c in chunks if c["madde_tur"] == "gecici"]
    asil_pool = [c for c in chunks if c["madde_tur"] == "asil"]

    rng = random.Random(seed)
    chosen = (
        rng.sample(ek_pool, min(10, len(ek_pool)))
        + rng.sample(gecici_pool, min(10, len(gecici_pool)))
        + rng.sample(asil_pool, min(20, len(asil_pool)))
    )
    return chosen


def generate_sample_report(
    chunks_path: Path = CHUNKS_PATH,
    hf_dir: Path = HF_DIR,
    out_path: Path = OUT_PATH,
    seed: int = 11,
    annotations: dict[str, tuple[str, str]] | None = None,
) -> Path:
    chosen = sample_chunks(chunks_path, seed=seed)
    raw_cache: dict[str, str] = {}
    annotations = annotations or {}

    lines = [
        f"# Geniş Katman Kalite Örneklemi (seed={seed}, N={len(chosen)})",
        "",
        "Havuz dağılımı: `10 ek_liste` + `10 gecici` + `20 asil` madde parçası.",
        "",
        "| # | Tür | `atif` | `chunk_id` | Parça (ilk 300 karakter) | HF Ham Metin (±150 karakter) | Durum | Kök Neden / Not |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for idx, c in enumerate(chosen, start=1):
        bid = c["belge_id"]
        if bid not in raw_cache:
            p = _hf_path_from_belge_id(Path(hf_dir), bid)
            raw_cache[bid] = json.loads(p.read_text(encoding="utf-8")).get("text", "") if p.exists() else ""
        raw_win = _find_raw_window(raw_cache[bid], c)
        preview = c["metin"][:300]
        durum, note = annotations.get(c["chunk_id"], ("incelenecek", ""))
        lines.append(
            f"| {idx} | `{c['madde_tur']}` | {_md_escape(c['atif'])} | `{c['chunk_id']}` | "
            f"{_md_escape(preview)} | {_md_escape(raw_win)} | {durum} | {_md_escape(note)} |"
        )

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunks", type=Path, default=CHUNKS_PATH)
    ap.add_argument("--hf-dir", type=Path, default=HF_DIR)
    ap.add_argument("--out", type=Path, default=OUT_PATH)
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()
    out = generate_sample_report(args.chunks, args.hf_dir, args.out, args.seed)
    print(f"Örneklem yazıldı -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
