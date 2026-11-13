"""Geniş katman arama ölçümü (LLM yok): eval/genis_sorular.jsonl (TASLAK; kullanıcı doğrulaması bekliyor).

Her soru için:
  yonlendirme : üretim yolu (build_context) soruyu geniş katmana yönlendirdi mi (derin katman eşiği geçilemedi ve
                geniş katman eşiği geçildi) — kapsam dışı sorularda hiçbir kanala gitmemesi beklenir
  bağlam      : beklenen "belge_id:madde_no" üretim yolunun bağlamında mı
  R@1 / R@5   : doğrudan geniş katman hibrit aramasında beklenen maddenin sırası (madde düzeyinde)
Küçük örneklem (15 + 3); taslak set olduğu için sonuçlar gösterge niteliğindedir.

Kullanım: python -m eval.genis_check
"""
from __future__ import annotations

import json
from pathlib import Path

from src.generate.answer import build_context, load_cfg
from src.retrieve.search import Searcher, attach_genis


def main() -> None:
    esik = load_cfg().get("esik")
    s = Searcher("hibrit", rerank=False)
    attach_genis(s)
    if s.genis is None:
        raise SystemExit("citelex_genis koleksiyonu yok (python -m src.index.build --mode genis --recreate --no-karar)")
    qs = [json.loads(l) for l in open("eval/genis_sorular.jsonl", encoding="utf-8")]
    rows = []
    for q in qs:
        hits, meta = build_context(s, q["soru"], esik)
        bag = {f"{h.payload['belge_id']}:{h.payload['madde_no']}" for h in hits}
        g = s.genis.search_context(q["soru"], "hybrid", k_mevzuat=5, k_karar=0, max_chars=None, mevzuat_tur=["kanun"])
        keys = list(dict.fromkeys(f"{h.payload['belge_id']}:{h.payload['madde_no']}" for h in g["mevzuat"]))
        rank = next((i + 1 for i, k in enumerate(keys) if k in q["beklenen"]), None)
        rows.append({"id": q["id"], "tur": q["tur"], "soru": q["soru"], "beklenen": q["beklenen"],
                     "kanallar": meta["kanallar"], "top1": meta["kanal_top1"],
                     "baglamda": bool(set(q["beklenen"]) & bag), "rank": rank, "ilk": keys[:3]})
    ic = [r for r in rows if r["tur"] != "kapsam_disi"]
    dis = [r for r in rows if r["tur"] == "kapsam_disi"]
    yon = sum(r["kanallar"] == ["genis"] for r in ic)
    L = ["# Geniş katman arama ölçümü (taslak set, LLM yok)", "",
         f"Eşik {esik}. Soru: {len(ic)} kapsam içi + {len(dis)} kapsam dışı (eval/genis_sorular.jsonl, TASLAK).", "",
         "| Ölçüt | Değer |", "|---|---|",
         f"| Geniş katmana yönlendirildi | {yon}/{len(ic)} |",
         f"| Beklenen madde üretim bağlamında | {sum(r['baglamda'] for r in ic)}/{len(ic)} |",
         f"| Doğrudan geniş arama R@1 | {sum(r['rank'] == 1 for r in ic)}/{len(ic)} |",
         f"| Doğrudan geniş arama R@5 | {sum(bool(r['rank']) for r in ic)}/{len(ic)} |",
         f"| Kapsam dışı: hiçbir kanala gitmedi (eşikte ret) | "
         f"{sum(max(r['top1'].values()) < esik for r in dis)}/{len(dis)} |", "",
         "| # | Soru | Beklenen | Kanal | Bağlamda | Sıra | İlk 3 |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['id']} | {r['soru'][:70]} | {', '.join(r['beklenen']) or 'kapsam dışı'} | {'/'.join(r['kanallar'])} "
                 f"({max(r['top1'].values()):.3f}) | {'✓' if r['baglamda'] else '✗'} | {r['rank'] or '—'} | {'; '.join(r['ilk'])} |")
    Path("results/genis_check.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(L[:11]))


if __name__ == "__main__":
    main()
