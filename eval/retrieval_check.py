"""Arama sağlık kontrolü: eval/retrieval_smoke.jsonl üzerinde dense / bm25 / hibrit.

Ölçüt: beklenen maddelerden biri (belge_id:madde_no) ilk k sonuçta mı (madde düzeyinde; fıkra
parçası da maddeyi sayar). Kapsam dışı sorularda isabet ölçülmez, ilk sonucun skoru raporlanır
("bilmiyorum" eşiği için ön bilgi).

NOT: 10 soru küçük bir örneklem; bu bir sağlık kontrolüdür, yöntem karşılaştırması değildir.
Beklenen maddeler taslaktır, kullanıcı kanun metninden doğrular.

Kullanım: python -m eval.retrieval_check --mode hibrit -k 5
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.retrieve.search import Searcher

METHODS = ["dense", "bm25", "hybrid"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="hibrit")
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--out", default="results/retrieval_check.md")
    args = ap.parse_args()

    qs = [json.loads(l) for l in open("eval/retrieval_smoke.jsonl", encoding="utf-8")]
    s = Searcher(args.mode)
    rows, hits = [], {m: 0 for m in METHODS}
    n_scored = sum(1 for q in qs if q["beklenen"])
    for q in qs:
        cells = []
        for m in METHODS:
            res = s.search(q["soru"], m, top_k=args.k)
            keys = [f"{h.payload['belge_id']}:{h.payload['madde_no']}" for h in res]
            if q["beklenen"]:
                rank = next((i + 1 for i, kk in enumerate(keys) if kk in q["beklenen"]), None)
                hits[m] += rank is not None
                cells.append(f"{rank}" if rank else "—")
            else:
                cells.append(f"top1 {res[0].score:.3f}: {res[0].payload['atif']}" if res else "boş")
        top = s.search(q["soru"], "hybrid", top_k=3)
        rows.append((q, cells, [h.payload["atif"] for h in top]))

    lines = [
        f"# Arama sağlık kontrolü ({args.mode}, ilk {args.k})", "",
        "Beklenen maddeler taslaktır (kullanıcı doğrulaması bekliyor). 10 soru: sağlık kontrolü, "
        "karşılaştırma değil. Hücre: beklenen maddenin sırası (— = ilk k'da yok).", "",
        "| # | Soru | Beklenen | " + " | ".join(METHODS) + " | Hibrit ilk 3 |",
        "|---|---|---|" + "---|" * len(METHODS) + "---|",
    ]
    for q, cells, top in rows:
        lines.append(f"| {q['id']} | {q['soru']} | {', '.join(q['beklenen']) or 'kapsam dışı'} | "
                     + " | ".join(cells) + f" | {'; '.join(top)} |")
    lines += ["", f"İlk {args.k}'te isabet ({n_scored} kapsam içi soru): "
              + ", ".join(f"{m} {hits[m]}/{n_scored}" for m in METHODS)]
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
