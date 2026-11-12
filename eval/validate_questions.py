"""eval/questions.jsonl doğrulayıcısı: beklenen kaynak ve kanıt derlemde gerçekten var mı?

Her kapsam içi soru için:
  - beklenen kaynak (belge_id:madde_no veya kvkk-karar-YYYY-N) derlemde bulunmalı,
  - kanit_kalip (regex) o kaynağın metninde eşleşmeli; eşleşen cümle `kanit` alanına yazılır,
  - anahtar gruplarının her birinden en az bir seçenek kanıt cümlesinde geçmeli
    (beklenen cevap derlemdeki metinden gelir; ajan hafızasından değil).
Beklenen cevaplar TASLAKTIR: bu betik yalnızca "soru derlemdeki metne dayanıyor" der; sorunun
hukuken doğru kurulduğunu kullanıcı kanun metninden doğrular (PLAN.md kuralı).

Yan fayda: derlem güncellenince (15 Kas) bu betik, değişen madde yüzünden eskiyen soruları yakalar.

Kullanım: python -m eval.validate_questions [--yaz]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from src.index.tokenize import turkish_lower

Q_PATH = Path("eval/questions.jsonl")


def load_corpus() -> dict[str, str]:
    """kaynak anahtarı -> metin. Mevzuat: belge_id:madde_no (asıl maddeler). Karar: belge_id (hüküm + değerlendirme)."""
    corpus: dict[str, str] = {}
    for l in open("data/processed/articles.jsonl", encoding="utf-8"):
        a = json.loads(l)
        if a["madde_tur"] != "asil" or a["mulga"]:
            continue
        corpus[f"{a['belge_id']}:{a['madde_no']}"] = "\n".join(f["metin"] for f in a["fikralar"] if not f["mulga"])
    for l in open("data/processed/chunks_karar.jsonl", encoding="utf-8"):
        c = json.loads(l)
        if c["bolum"] in ("hukum", "degerlendirme"):
            corpus[c["belge_id"]] = corpus.get(c["belge_id"], "") + "\n" + c["metin"]
    return corpus


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", turkish_lower(s))


def find_evidence(text: str, pattern: str) -> str | None:
    flat = re.sub(r"\s+", " ", text)
    m = re.search(pattern, flat, re.I)
    if not m:
        return None
    # Eşleşmenin etrafında ±250 karakterlik pencere, kelime sınırına hizalı (cümle sınırı aramak
    # uzun hukuk cümlelerinde eşleşmeyi pencerenin dışında bırakıyordu).
    start = max(0, m.start() - 250)
    end = min(len(flat), m.end() + 250)
    if start > 0:
        start = flat.find(" ", start) + 1
    if end < len(flat):
        end = flat.rfind(" ", 0, end)
    return ("… " if start > 0 else "") + flat[start:end].strip() + (" …" if end < len(flat) else "")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--yaz", action="store_true", help="kanit alanlarını dosyaya yaz")
    args = ap.parse_args()
    corpus = load_corpus()
    qs = [json.loads(l) for l in open(Q_PATH, encoding="utf-8")]
    bad = 0
    ids = [q["id"] for q in qs]
    assert len(ids) == len(set(ids)), "tekrarlanan id"
    for q in qs:
        if q["tur"] == "kapsam_disi":
            continue
        src = q["beklenen"][0]
        if any(b not in corpus for b in q["beklenen"]):
            print(f"HATA {q['id']}: kaynak yok {[b for b in q['beklenen'] if b not in corpus]}")
            bad += 1
            continue
        ev = find_evidence(corpus[src], q["kanit_kalip"])
        if ev is None:
            print(f"HATA {q['id']}: kanıt kalıbı eşleşmedi ({src}): {q['kanit_kalip']}")
            bad += 1
            continue
        eksik = [g for g in q["anahtar"] if not any(norm(alt) in norm(ev) for alt in g)]
        if eksik:
            print(f"HATA {q['id']}: anahtar kanıtta yok {eksik} | kanıt: {ev[:160]}")
            bad += 1
            continue
        q["kanit"] = ev
    n_in = sum(q["tur"] != "kapsam_disi" for q in qs)
    print(f"{len(qs)} soru ({n_in} kapsam içi, {len(qs) - n_in} kapsam dışı); {bad} hata")
    if args.yaz and not bad:
        with Q_PATH.open("w", encoding="utf-8", newline="\n") as fh:
            for q in qs:
                fh.write(json.dumps(q, ensure_ascii=False) + "\n")
        print("kanıtlar yazıldı")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
