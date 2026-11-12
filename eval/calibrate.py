""""Bilmiyorum" arama eşiğinin kalibrasyonu (eval setinden AYRI: eval/calibration.jsonl).

Sinyal: dense top-1 kosinüs benzerliği (mevzuat ve karar kanallarının en büyüğü).
Kural: eşik = kapsam içi soruların en düşük skoru - PAY. Yani kalibrasyon setinde cevaplanabilir
hiçbir soru eşiğe takılmaz; eşik yalnızca konudan uzak soruları keser. Konuya yakın ama derlemde
cevabı olmayan sorular bu katmanı geçer; onları LLM'in CEVAP_YOK kuralı yakalar (ikinci katman).

Kullanım: python -m eval.calibrate [--yaz]     (--yaz: eşiği configs/answer.json'a yazar)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.retrieve.search import MEVZUAT_TURLERI, Searcher

PAY = 0.02
CFG = Path("configs/answer.json")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--yaz", action="store_true")
    args = ap.parse_args()
    qs = [json.loads(l) for l in open("eval/calibration.jsonl", encoding="utf-8")]
    s = Searcher("hibrit")
    rows = []
    for q in qs:
        m = s.search(q["soru"], "dense", top_k=1, belge_tur=MEVZUAT_TURLERI)
        k = s.search(q["soru"], "dense", top_k=1, belge_tur=["karar"])
        best = max(m + k, key=lambda h: h.score)
        rows.append((q, best.score, best.payload["atif"]))
    ic = [sc for q, sc, _ in rows if q["kapsam"] == "ic"]
    esik = round(min(ic) - PAY, 3)
    lines = ["# \"Bilmiyorum\" eşiği kalibrasyonu", "",
             f"Sinyal: dense top-1 benzerliği. Eşik = kapsam içi en düşük skor ({min(ic):.3f}) - {PAY} = **{esik}**.", "",
             "| # | Kapsam | Soru | dense top-1 | En yakın kaynak | Eşik sonucu |", "|---|---|---|---|---|---|"]
    for q, sc, atif in sorted(rows, key=lambda r: -r[1]):
        lines.append(f"| {q['id']} | {q['kapsam']} | {q['soru']} | {sc:.3f} | {atif} | {'geçer' if sc >= esik else 'KESİLİR'} |")
    for grp in ["dis_yakin", "dis_uzak"]:
        g = [sc for q, sc, _ in rows if q["kapsam"] == grp]
        lines.append(f"\n{grp}: {sum(sc < esik for sc in g)}/{len(g)} soru eşikte kesiliyor (skor aralığı {min(g):.3f}–{max(g):.3f})")
    lines.append("\nNot: 10 soru; eşik kaba bir ilk filtredir. Eşiği geçen kapsam dışı sorular LLM katmanına (CEVAP_YOK) kalır.")
    Path("results/calibration.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    if args.yaz:
        cfg = json.loads(CFG.read_text(encoding="utf-8"))
        cfg["esik"] = esik
        CFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"\nconfigs/answer.json: esik={esik}")


if __name__ == "__main__":
    main()
