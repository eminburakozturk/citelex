"""Reranker ölçümü: hibrit arama adayları (ilk 30 parça) olduğu gibi mi, çapraz kodlayıcıyla yeniden sıralanmış mı?

Sorular ve ölçüt eval/gate.py ile aynı (beklenen kaynağı olan 63 soru; mevzuat madde düzeyinde, karar karar düzeyinde).
Ölçülen: beklenen kaynağın sırası -> recall@1/3/5 ve MRR (ilk 10 içinde; dışındaysa 0). Ayrıca sorgu başı rerank süresi.
Reranker: BAAI/bge-reranker-v2-m3 (çok dilli; Türkçe destekli). Eşik/prompt bu sette AYARLANMAZ; yalnız ölçüm.

Kullanım: python -m eval.rerank_compare [--aday 30]
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from eval.gate import SORU_DOSYALARI, kanal
from src.retrieve.search import MEVZUAT_TURLERI, Searcher

MODEL = "BAAI/bge-reranker-v2-m3"


def rank_of(keys: list[str], beklenen: list[str]) -> int | None:
    return next((i + 1 for i, k in enumerate(keys) if k in beklenen), None)


def key(p: dict, kn: str) -> str:
    return p["belge_id"] if kn == "karar" else f"{p['belge_id']}:{p['madde_no']}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aday", type=int, default=30)
    args = ap.parse_args()
    from FlagEmbedding import FlagReranker
    rr = FlagReranker(MODEL, use_fp16=True)
    s = Searcher("hibrit")
    qs = [json.loads(l) for f in SORU_DOSYALARI for l in open(f, encoding="utf-8")]
    qs = [q for q in qs if q["beklenen"]]
    rows, sure = [], []
    for q in qs:
        kn = kanal(q["beklenen"])
        turler = ["karar"] if kn == "karar" else MEVZUAT_TURLERI
        hits = s.search(q["soru"], "hybrid", top_k=args.aday, belge_tur=turler)
        t = time.time()
        # Payload'da embed_text yok: atıf + başlık + metin (belge/madde bağlamı reranker'a da verilsin)
        scores = rr.compute_score([[q["soru"], f"{h.payload['atif']} {h.payload.get('baslik') or ''}\n{h.payload['metin']}"]
                                   for h in hits], normalize=True) if hits else []
        sure.append(time.time() - t)
        rer = [h for _, h in sorted(zip(scores, hits), key=lambda x: -x[0])]
        once = list(dict.fromkeys(key(h.payload, kn) for h in hits))
        sonra = list(dict.fromkeys(key(h.payload, kn) for h in rer))
        rows.append({"id": q["id"], "kanal": kn, "once": rank_of(once, q["beklenen"]), "sonra": rank_of(sonra, q["beklenen"])})

    def ozet(rs: list[dict], col: str) -> dict:
        n = len(rs)
        r = [x[col] for x in rs]
        return {"n": n, **{f"r@{k}": sum(1 for v in r if v and v <= k) for k in (1, 3, 5)},
                "mrr": round(sum(1 / v for v in r if v and v <= 10) / n, 3)}

    L = [f"# Reranker ölçümü ({MODEL}, hibrit ilk {args.aday} aday)", "",
         "Sorular: eval/questions.jsonl + eval/retrieval_smoke.jsonl (beklenen kaynağı olanlar). Sıra madde/karar "
         "düzeyinde (aynı maddenin parçaları tek sayılır). MRR ilk 10'a göre.", "",
         "| Kanal | Yöntem | n | R@1 | R@3 | R@5 | MRR |", "|---|---|---|---|---|---|---|"]
    for kn in ("mevzuat", "karar"):
        rs = [r for r in rows if r["kanal"] == kn]
        for col, ad in (("once", "hibrit"), ("sonra", "hibrit + reranker")):
            o = ozet(rs, col)
            L.append(f"| {kn} | {ad} | {o['n']} | {o['r@1']} | {o['r@3']} | {o['r@5']} | {o['mrr']} |")
    deg = [r for r in rows if r["once"] != r["sonra"]]
    L += ["", f"Rerank süresi: medyan {sorted(sure)[len(sure) // 2]:.2f} sn/sorgu ({args.aday} aday, GPU fp16).", "",
          "## Sırası değişen sorular", "", "| # | Kanal | Önce | Sonra |", "|---|---|---|---|"]
    L += [f"| {r['id']} | {r['kanal']} | {r['once'] or '—'} | {r['sonra'] or '—'} |" for r in deg]
    Path("results/rerank_compare.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
