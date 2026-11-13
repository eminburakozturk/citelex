"""Arama regresyonu kapısı (CI): isabeti düşüren değişiklik çıkış kodu 1 ile kırmızı olur.

İki motor:
  bm25   : (CI, varsayılan) Qdrant ve bge-m3 GEREKMEZ. eval/fixtures altındaki derlem anlık görüntüsünden
           (articles + karar parçaları) parçalar BELLEKTE yeniden üretilir (src/ingest/chunk.py), BM25 ağırlıkları
           üretimdeki kodla (src/index/bm25.py, Qdrant'ın IDF formülü) hesaplanır. Böylece parçalama, tokenizer
           ve BM25 değişiklikleri CI'da yakalanır. Dense/hibrit kanal burada ÖLÇÜLMEZ.
  qdrant : (yerel) gerçek hibrit arama, Searcher.search_context ile; Qdrant + bge-m3 gerekir.
Ölçüt (iki kanal, src/retrieve/search.py ile aynı): mevzuat = beklenen "belge_id:madde_no" ilk k FARKLI maddede mi;
karar = beklenen karar ilk 3 FARKLI kararda mı. Sorular: eval/questions.jsonl + eval/retrieval_smoke.jsonl
(beklenen kaynağı olanlar). Kapı: her kanalda isabet sayısı temel değerin (eval/gate_baseline.json) altına düşerse kırmızı.

Kullanım:
  python -m eval.gate                       # kontrol (CI)
  python -m eval.gate --temel-guncelle      # bilinçli iyileşme/değişiklikten sonra temel değeri yaz
  python -m eval.gate --anlik-goruntu       # data/processed'tan eval/fixtures'ı yenile (derlem değişince)
  python -m eval.gate --motor qdrant        # yerel hibrit ölçüm (temel değer ayrı anahtarda)
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import shutil
import sys
from collections import Counter
from pathlib import Path

from src.index import bm25
from src.index.tokenize import tokenize
from src.ingest.chunk import chunk_article

FIX = Path("eval/fixtures")
BASELINE = Path("eval/gate_baseline.json")
SORU_DOSYALARI = ["eval/questions.jsonl", "eval/retrieval_smoke.jsonl"]
MEVZUAT_TURLERI = {"kanun", "yonetmelik", "teblig"}
K_MEVZUAT, K_KARAR = 5, 3


def load_gz(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return [json.loads(l) for l in fh]


def snapshot() -> None:
    FIX.mkdir(parents=True, exist_ok=True)
    for src in ["articles.jsonl", "chunks_karar.jsonl"]:
        with open(f"data/processed/{src}", "rb") as fi, open(FIX / f"{src}.gz", "wb") as raw, \
                gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as fo:  # sabit başlık: aynı veri = aynı dosya
            shutil.copyfileobj(fi, fo)
        print(f"{src} -> {FIX / (src + '.gz')}")


class MemoryBM25:
    """Qdrant'taki BM25 kanalının bellek içi eşi: doc TF ağırlığı istemcide, IDF = ln(1 + (N-n+0.5)/(n+0.5))."""

    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        texts = [c["embed_text"] for c in chunks]
        p = bm25.fit(texts)
        self.vecs: list[dict[int, float]] = []
        df: Counter = Counter()
        for t in texts:
            idx, val = bm25.doc_vector(t, p)
            self.vecs.append(dict(zip(idx, val)))
            df.update(idx)
        n = len(texts)
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    def search(self, query: str, turler: set[str], top_k: int) -> list[dict]:
        q, _ = bm25.query_vector(query)
        scored = []
        for c, v in zip(self.chunks, self.vecs):
            if c["mulga"] or c["diger_kanuna_islendi"] or c["belge_tur"] not in turler:
                continue
            s = sum(v[t] * self.idf[t] for t in q if t in v)
            if s > 0:
                scored.append((s, c))
        scored.sort(key=lambda x: -x[0])
        return [c for _, c in scored[:top_k]]


def keys_bm25(eng: MemoryBM25, soru: str) -> dict[str, list[str]]:
    mev = eng.search(soru, MEVZUAT_TURLERI, K_MEVZUAT * 3)
    madde = list(dict.fromkeys(f"{c['belge_id']}:{c['madde_no']}" for c in mev))[:K_MEVZUAT]
    karar = list(dict.fromkeys(c["belge_id"] for c in eng.search(soru, {"karar"}, 30)))[:K_KARAR]
    return {"mevzuat": madde, "karar": karar}


def keys_qdrant(searcher, soru: str) -> dict[str, list[str]]:
    ctx = searcher.search_context(soru, "hybrid", k_mevzuat=K_MEVZUAT, k_karar=K_KARAR, max_chars=None)
    return {"mevzuat": list(dict.fromkeys(f"{h.payload['belge_id']}:{h.payload['madde_no']}" for h in ctx["mevzuat"])),
            "karar": list(dict.fromkeys(h.payload["belge_id"] for h in ctx["karar"]))}


def kanal(beklenen: list[str]) -> str:
    return "karar" if all(b.startswith("kvkk-karar-") for b in beklenen) else "mevzuat"


def run(motor: str) -> tuple[dict, list[dict]]:
    qs = [json.loads(l) for f in SORU_DOSYALARI for l in open(f, encoding="utf-8")]
    qs = [q for q in qs if q["beklenen"]]
    if motor == "bm25":
        arts = load_gz(FIX / "articles.jsonl.gz")
        chunks = [c for a in arts for c in chunk_article(a, "hibrit", 1500)] + load_gz(FIX / "chunks_karar.jsonl.gz")
        eng = MemoryBM25(chunks)
        finder = lambda s: keys_bm25(eng, s)  # noqa: E731
    else:
        from src.retrieve.search import Searcher
        searcher = Searcher("hibrit")
        finder = lambda s: keys_qdrant(searcher, s)  # noqa: E731
    sonuc = {"mevzuat": [0, 0], "karar": [0, 0]}
    satirlar = []
    for q in qs:
        kn = kanal(q["beklenen"])
        bulunan = finder(q["soru"])[kn]
        isabet = any(b in bulunan for b in q["beklenen"])
        sonuc[kn][0] += isabet
        sonuc[kn][1] += 1
        satirlar.append({"id": q["id"], "kanal": kn, "isabet": isabet})
    return {k: {"isabet": v[0], "n": v[1]} for k, v in sonuc.items()}, satirlar


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--motor", choices=["bm25", "qdrant"], default="bm25")
    ap.add_argument("--temel-guncelle", action="store_true")
    ap.add_argument("--anlik-goruntu", action="store_true")
    args = ap.parse_args()
    if args.anlik_goruntu:
        snapshot()
    olcum, satirlar = run(args.motor)
    temel_hepsi = json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else {}
    temel = temel_hepsi.get(args.motor)
    print(f"motor={args.motor}")
    for kn, m in olcum.items():
        t = f" (temel {temel[kn]['isabet']}/{temel[kn]['n']})" if temel else ""
        print(f"  {kn}: {m['isabet']}/{m['n']}{t}")
    print("  kaçanlar: " + (", ".join(s["id"] for s in satirlar if not s["isabet"]) or "yok"))
    if args.temel_guncelle:
        temel_hepsi[args.motor] = olcum
        BASELINE.write_text(json.dumps(temel_hepsi, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"temel değer yazıldı -> {BASELINE}")
        return 0
    if not temel:
        print("temel değer yok: önce --temel-guncelle")
        return 1
    dusen = [kn for kn in olcum if olcum[kn]["isabet"] < temel[kn]["isabet"]]
    if dusen:
        print(f"KIRMIZI: isabet düştü ({', '.join(dusen)})")
        return 1
    print("YEŞİL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
