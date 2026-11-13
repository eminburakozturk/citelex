"""Geniş katman taslak soru setini (eval/genis_sorular.jsonl) doğrular ve --yaz ile kanıtı yazar."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from src.index.tokenize import turkish_lower

ARTICLES = Path("data/processed/articles_genis.jsonl")
SORULAR = Path("eval/genis_sorular.jsonl")
DERIN_KANUNLAR = {"kanun-6698", "kanun-4857", "kanun-6331", "kanun-1475"}


def load_corpus(path: Path = ARTICLES) -> dict[str, str]:
    """articles_genis.jsonl içindeki yürürlükteki maddeleri belge_id:madde_no -> metin olarak yükler."""
    corpus: dict[str, str] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            a = json.loads(line)
            if a.get("mulga") or a.get("madde_tur") not in ("asil", "ek", "gecici"):
                continue
            metin = "\n".join(
                f["metin"] for f in a.get("fikralar", []) if not f.get("mulga") and f.get("metin")
            )
            if metin:
                corpus[f"{a['belge_id']}:{a['madde_no']}"] = metin
    return corpus


def find_evidence(text: str, pattern: str, window: int = 250) -> str | None:
    """Metinde kalıp eşleşmesi etrafından kelime sınırına hizalanmış ±250 karakterlik kanıt çıkarır."""
    m = re.search(pattern, text, re.IGNORECASE | re.UNICODE)
    if not m:
        return None
    start = max(0, m.start() - window)
    end = min(len(text), m.end() + window)
    if start > 0:
        sp = text.find(" ", start)
        if 0 < sp < m.start():
            start = sp + 1
    if end < len(text):
        sp = text.rfind(" ", m.end(), end)
        if sp > m.end():
            end = sp
    snippet = text[start:end].strip()
    if start > 0:
        snippet = "… " + snippet
    if end < len(text):
        snippet = snippet + " …"
    return snippet


def dogrula(sorular_path: Path = SORULAR, articles_path: Path = ARTICLES, yaz: bool = False) -> tuple[int, int, list[str]]:
    """Soruları doğrular; (kapsam_ici_sayisi, kapsam_disi_sayisi, hatalar) döndürür."""
    corpus = load_corpus(articles_path)
    rows = [json.loads(line) for line in sorular_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    hatalar: list[str] = []
    gorulen_kanunlar: set[str] = set()
    kapsam_ici = 0
    kapsam_disi = 0

    for q in rows:
        qid = q.get("id", "?")
        tur = q.get("tur")
        beklenen = q.get("beklenen") or []

        if tur == "kapsam_disi":
            kapsam_disi += 1
            if beklenen:
                hatalar.append(f"{qid}: kapsam_disi soruda beklenen boş olmalı")
            continue

        kapsam_ici += 1
        if not beklenen:
            hatalar.append(f"{qid}: beklenen boş")
            continue

        anahtar_ref = beklenen[0]
        belge_id = anahtar_ref.split(":", 1)[0]
        if belge_id in DERIN_KANUNLAR:
            hatalar.append(f"{qid}: derin katman kanunu yasak ({belge_id})")
        if belge_id in gorulen_kanunlar:
            hatalar.append(f"{qid}: aynı kanundan birden fazla soru var ({belge_id})")
        gorulen_kanunlar.add(belge_id)

        for ref in beklenen:
            if ref not in corpus:
                hatalar.append(f"{qid}: hedef bulunamadı ({ref})")

        if anahtar_ref not in corpus:
            continue

        kalip = q.get("kanit_kalip") or ""
        ev = find_evidence(corpus[anahtar_ref], kalip) if kalip else None
        if not ev:
            hatalar.append(f"{qid}: kanit_kalip eşleşmedi ({anahtar_ref})")
            continue

        ev_norm = turkish_lower(ev)
        for grup in q.get("anahtar") or []:
            if not any(turkish_lower(alt) in ev_norm for alt in grup):
                hatalar.append(f"{qid}: anahtar grubu kanıtta yok -> {grup}")

        if yaz:
            q["kanit"] = ev
        elif not q.get("kanit") or q["kanit"] != ev:
            hatalar.append(f"{qid}: dosyadaki 'kanit' metni find_evidence çıktısıyla birebir aynı değil (--yaz çalıştırın)")

    if yaz and not hatalar:
        sorular_path.write_text(
            "\n".join(json.dumps(q, ensure_ascii=False) for q in rows) + "\n",
            encoding="utf-8",
        )

    return kapsam_ici, kapsam_disi, hatalar


def main() -> None:
    p = argparse.ArgumentParser(description="Geniş katman soru setini doğrular.")
    p.add_argument("--yaz", action="store_true", help="Doğrulanan kanıtları dosyaya yazar.")
    p.add_argument("--sorular", type=Path, default=SORULAR)
    p.add_argument("--articles", type=Path, default=ARTICLES)
    args = p.parse_args()

    ici, disi, hatalar = dogrula(args.sorular, args.articles, yaz=args.yaz)
    toplam = ici + disi
    print(f"Doğrulama: {toplam} soru ({ici} kapsam içi, {disi} kapsam dışı); {len(hatalar)} hata")
    for h in hatalar:
        print("  HATA:", h)
    if hatalar:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
