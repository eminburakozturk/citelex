"""Parçalama kontrol raporu -> results/ingest_report.md (git'e girer)."""
from __future__ import annotations

import json
import random
import statistics
from collections import Counter
from pathlib import Path


def load(p: str) -> list[dict]:
    return [json.loads(l) for l in open(p, encoding="utf-8")]


def main() -> None:
    arts = load("data/processed/articles.jsonl")
    lines = ["# Parçalama raporu", "", "Kaynak: mevzuat.gov.tr PDF (data/raw, 11 Kasım 2026'da indirildi)", ""]
    lines += ["| Belge | Tür | Asıl | Ek | Geçici | Mülga madde | Başka kanuna işlenmiş | Fıkra | Dipnot |",
              "|---|---|---|---|---|---|---|---|---|"]
    for k in dict.fromkeys(a["belge_id"] for a in arts):
        xs = [a for a in arts if a["belge_id"] == k]
        t = Counter(a["madde_tur"] for a in xs)
        lines.append(f"| {xs[0]['kisa_ad']} | {xs[0]['belge_tur']} | {t['asil']} | {t['ek']} | {t['gecici']} | "
                     f"{sum(a['mulga'] for a in xs)} | {sum(a['diger_kanuna_islendi'] for a in xs)} | "
                     f"{sum(len(a['fikralar']) for a in xs)} | {sum(len(a['dipnotlar']) for a in xs)} |")
    lines += ["", "| Mod | Parça | Aktif | Medyan karakter | Maks karakter |", "|---|---|---|---|---|"]
    for mode in ["madde", "hibrit", "fikra"]:
        p = Path(f"data/processed/chunks_{mode}.jsonl")
        if not p.exists():
            continue
        cs = load(str(p))
        aktif = [c for c in cs if not (c["mulga"] or c["diger_kanuna_islendi"])]
        L = [len(c["metin"]) for c in aktif]
        lines.append(f"| {mode} | {len(cs)} | {len(aktif)} | {int(statistics.median(L))} | {max(L)} |")
    lines += ["", "Mülga maddeler: " + ", ".join(f"{a['kisa_ad']} m. {a['madde_no']}" for a in arts if a["mulga"]),
              "", "Mülga fıkralar: " + ", ".join(f"{a['kisa_ad']} m. {a['madde_no']}/{f['fikra_no']}"
                                                 for a in arts if not a["mulga"] for f in a["fikralar"] if f["mulga"])]
    random.seed(42)
    cs = [c for c in load("data/processed/chunks_hibrit.jsonl") if not c["mulga"]]
    lines += ["", "## Rastgele 5 örnek (hibrit, seed 42)", ""]
    for c in random.sample(cs, 5):
        lines += [f"**{c['atif']}** — {c['baslik']}", "", "> " + c["metin"][:400].replace("\n", "\n> "), ""]
    out = Path("results/ingest_report.md")
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out.read_text(encoding="utf-8")[:1800])


if __name__ == "__main__":
    main()
