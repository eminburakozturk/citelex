"""Arama karşılaştırma deneyleri (19 Kas): parçalama (madde / fıkra / hibrit) × yöntem (dense / BM25 / hibrit RRF),
ve sözcüksel kanal: BM25 (bizim tokenizer) vs bge-m3 sparse (öğrenilmiş sözcük ağırlıkları).

Sorular ve ölçüt eval/gate.py ile aynı: beklenen kaynağı olan 63 soru (eval seti + sağlık seti); mevzuat madde düzeyinde
ilk 5 farklı madde, karar düzeyinde ilk 3 farklı karar (src/retrieve/search.py search_context). R@1, R@k, MRR@k.
Deney 2 bellekte: hibrit parçalar üzerinde iki sözcüksel yöntemin tek başına sıralaması (mevzuat kanalı, aktif parçalar).
NOT: eşik/prompt bu sonuçlara göre ayarlanmaz; küçük örneklem (51 mevzuat + 12 karar sorusu), farklar 1-2 soru ise gürültüdür.

Kullanım: python -m eval.compare_retrieval
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from eval.gate import FIX, SORU_DOSYALARI, MEVZUAT_TURLERI, MemoryBM25, kanal, load_gz
from src.ingest.chunk import chunk_article

MODES = ["madde", "fikra", "hibrit"]
METHODS = ["dense", "bm25", "hybrid"]


def sorular() -> list[dict]:
    qs = [json.loads(l) for f in SORU_DOSYALARI for l in open(f, encoding="utf-8")]
    return [q for q in qs if q["beklenen"]]


def metrik(ranks: list[int | None], k: int) -> tuple[int, int, float]:
    return (sum(1 for r in ranks if r == 1), sum(1 for r in ranks if r and r <= k),
            round(sum(1 / r for r in ranks if r and r <= k) / len(ranks), 3))


def deney1(qs: list[dict]) -> list[str]:
    from src.retrieve.search import Searcher
    L = ["## 1. Parçalama × yöntem (Qdrant, iki kanal)", "",
         "| Parçalama | Yöntem | Mevzuat R@1 | Mevzuat R@5 | Mevzuat MRR | Karar R@1 | Karar R@3 | Süre (sn/soru) |",
         "|---|---|---|---|---|---|---|---|"]
    emb = None
    for mode in MODES:
        s = Searcher(mode, emb)
        emb = s.embedder
        for m in METHODS:
            rk = {"mevzuat": [], "karar": []}
            t = time.time()
            for q in qs:
                kn = kanal(q["beklenen"])
                ctx = s.search_context(q["soru"], m, k_mevzuat=5, k_karar=3, max_chars=None)
                keys = list(dict.fromkeys(h.payload["belge_id"] if kn == "karar" else
                                          f"{h.payload['belge_id']}:{h.payload['madde_no']}" for h in ctx[kn]))
                rk[kn].append(next((i + 1 for i, x in enumerate(keys) if x in q["beklenen"]), None))
            sn = (time.time() - t) / len(qs)
            a, b, c = metrik(rk["mevzuat"], 5)
            d, e, _ = metrik(rk["karar"], 3)
            L.append(f"| {mode} | {m} | {a}/{len(rk['mevzuat'])} | {b}/{len(rk['mevzuat'])} | {c} | "
                     f"{d}/{len(rk['karar'])} | {e}/{len(rk['karar'])} | {sn:.2f} |")
            print(L[-1], flush=True)
    return L


def deney2(qs: list[dict]) -> list[str]:
    from FlagEmbedding import BGEM3FlagModel
    arts = load_gz(FIX / "articles.jsonl.gz")
    chunks = [c for a in arts for c in chunk_article(a, "hibrit", 1500)]
    aktif = [c for c in chunks if not (c["mulga"] or c["diger_kanuna_islendi"]) and c["belge_tur"] in MEVZUAT_TURLERI]
    bm = MemoryBM25(aktif)
    m3 = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
    t = time.time()
    doc_w = m3.encode([c["embed_text"] for c in aktif], return_dense=False, return_sparse=True,
                      batch_size=16, max_length=1024)["lexical_weights"]
    enc_sn = time.time() - t
    qm = [q for q in qs if kanal(q["beklenen"]) == "mevzuat"]
    q_w = m3.encode([q["soru"] for q in qm], return_dense=False, return_sparse=True)["lexical_weights"]
    rk_bm, rk_m3 = [], []
    for q, qw in zip(qm, q_w):
        keys_bm = list(dict.fromkeys(f"{c['belge_id']}:{c['madde_no']}" for c in bm.search(q["soru"], MEVZUAT_TURLERI, 15)))[:5]
        sc = sorted(((sum(w * dw.get(t, 0.0) for t, w in qw.items()), c) for dw, c in zip(doc_w, aktif)),
                    key=lambda x: -x[0])[:15]
        keys_m3 = list(dict.fromkeys(f"{c['belge_id']}:{c['madde_no']}" for s, c in sc if s > 0))[:5]
        rk_bm.append(next((i + 1 for i, x in enumerate(keys_bm) if x in q["beklenen"]), None))
        rk_m3.append(next((i + 1 for i, x in enumerate(keys_m3) if x in q["beklenen"]), None))
    L = ["", "## 2. Sözcüksel kanal: BM25 vs bge-m3 sparse (bellekte, hibrit parçalar, mevzuat kanalı)", "",
         f"{len(aktif)} aktif mevzuat parçası; bge-m3 sparse kodlama {enc_sn:.0f} sn (GPU fp16).", "",
         "| Yöntem | R@1 | R@5 | MRR@5 |", "|---|---|---|---|"]
    for ad, rk in (("BM25 (Türkçe tokenizer)", rk_bm), ("bge-m3 sparse", rk_m3)):
        a, b, c = metrik(rk, 5)
        L.append(f"| {ad} | {a}/{len(rk)} | {b}/{len(rk)} | {c} |")
    print("\n".join(L), flush=True)
    return L


def main() -> None:
    qs = sorular()
    L = ["# Arama karşılaştırma deneyleri", "",
         f"Sorular: {len(qs)} (beklenen kaynağı olanlar: eval/questions.jsonl + eval/retrieval_smoke.jsonl). "
         "Küçük örneklem: 1-2 soruluk farklar gürültüdür. Reranker kapalı (ayrı ölçüm: results/rerank_compare.md).", ""]
    L += deney1(qs)
    L += deney2(qs)
    Path("results/compare_retrieval.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
