"""Arama sağlık kontrolü: eval/retrieval_smoke.jsonl üzerinde dense / bm25 / hibrit.

İki kanal ayrı ölçülür (src/retrieve/search.py: search_context):
  mevzuat : beklenen "belge_id:madde_no" mevzuat kanalının ilk k sonucunda mı (madde düzeyinde;
            fıkra parçası da maddeyi sayar)
  karar   : beklenen "kvkk-karar-YYYY-N" karar kanalında ilk k_karar karar içinde mi
Kapsam dışı sorularda isabet ölçülmez, mevzuat kanalının ilk sonucunun skoru raporlanır.
--tek-havuz: kanalları ayırmadan tek listede ölçer (kararların mevzuatı dışarı ittiğini göstermek için).

NOT: küçük örneklem; bu bir sağlık kontrolüdür, yöntem karşılaştırması değildir.
Beklenenler ve kanıt cümleleri eval/retrieval_smoke.jsonl içinde (durum=ajan_dogruladi).

Kullanım: python -m eval.retrieval_check --mode hibrit -k 5
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.retrieve.search import Searcher

METHODS = ["dense", "bm25", "hybrid"]
K_KARAR = 3


def key(h) -> str:
    p = h.payload
    return p["belge_id"] if p["belge_tur"] == "karar" else f"{p['belge_id']}:{p['madde_no']}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="hibrit")
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--tek-havuz", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    out = args.out or ("results/retrieval_check_tek_havuz.md" if args.tek_havuz else "results/retrieval_check.md")

    qs = [json.loads(l) for l in open("eval/retrieval_smoke.jsonl", encoding="utf-8")]
    s = Searcher(args.mode, rerank=False)   # temel değerler reranker'sız ölçüldü; CPU'da reranker çok yavaş
    kanallar = ["mevzuat", "karar"]
    hits = {kn: {m: 0 for m in METHODS} for kn in kanallar}
    n = {kn: sum(1 for q in qs if q["beklenen"] and q.get("kanal", "mevzuat") == kn) for kn in kanallar}
    rows = []
    for q in qs:
        kanal = q.get("kanal", "mevzuat")
        cells = []
        for m in METHODS:
            if args.tek_havuz:
                res = s.search(q["soru"], m, top_k=args.k)
                keys = list(dict.fromkeys(key(h) for h in res))
            else:
                ctx = s.search_context(q["soru"], m, k_mevzuat=args.k, k_karar=K_KARAR)
                res = ctx[kanal]
                keys = list(dict.fromkeys(key(h) for h in res))
            if q["beklenen"]:
                rank = next((i + 1 for i, kk in enumerate(keys) if kk in q["beklenen"]), None)
                hits[kanal][m] += rank is not None
                cells.append(f"{rank}" if rank else "—")
            else:
                cells.append(f"top1 {res[0].score:.3f}: {res[0].payload['atif']}" if res else "boş")
        if args.tek_havuz:
            top = [h.payload["atif"] for h in s.search(q["soru"], "hybrid", top_k=3)]
        else:
            ctx = s.search_context(q["soru"], "hybrid", k_mevzuat=2, k_karar=1, per_karar=1)
            top = [h.payload["atif"] for h in ctx["mevzuat"] + ctx["karar"]]
        rows.append((q, kanal, cells, top))

    baslik = "tek havuz" if args.tek_havuz else f"iki kanal: mevzuat ilk {args.k}, karar ilk {K_KARAR} karar"
    lines = [
        f"# Arama sağlık kontrolü ({args.mode}, {baslik})", "",
        "Beklenenler ajan tarafından ayrıştırılmış metinden doğrulandı (kanit alanı); bağımsız insan doğrulaması değil. "
        "Küçük örneklem: sağlık kontrolü, karşılaştırma değil. Hücre: beklenenin sırası (— = yok).", "",
        "| # | Kanal | Soru | Beklenen | " + " | ".join(METHODS) + " | Hibrit: ilk sonuçlar |",
        "|---|---|---|---|" + "---|" * len(METHODS) + "---|",
    ]
    for q, kanal, cells, top in rows:
        lines.append(f"| {q['id']} | {kanal} | {q['soru']} | {', '.join(q['beklenen']) or 'kapsam dışı'} | "
                     + " | ".join(cells) + f" | {'; '.join(top)} |")
    lines.append("")
    for kn in kanallar:
        if n[kn]:
            lines.append(f"{kn} isabet ({n[kn]} soru): " + ", ".join(f"{m} {hits[kn][m]}/{n[kn]}" for m in METHODS))
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
