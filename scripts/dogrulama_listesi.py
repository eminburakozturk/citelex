"""Kullanıcı doğrulaması için kontrol listesi: eval/questions.jsonl (+ eval/genis_sorular.jsonl) -> eval/DOGRULAMA.md

Her soru için: beklenen kaynak, kanıt cümlesi (derlem metninden), cevapta aranan anahtar ifadeler, resmî metin bağlantısı
ve işaretlenecek kutular. Kullanıcı resmî metne bakıp kutuları işaretler; notu "Not:" satırına yazar.
Sonra: python -m scripts.dogrulama_listesi --oku  ->  işaretlenmeyen/itiraz edilen soruları listeler.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

OUT = Path("eval/DOGRULAMA.md")
SETLER = [("eval/questions.jsonl", "Ana değerlendirme seti (56 soru)"),
          ("eval/genis_sorular.jsonl", "Geniş katman seti (18 soru, taslak)")]
KARAR_URL = "https://www.kvkk.gov.tr/Icerik/5406"


def kaynak_url(anahtar: str, sources: dict) -> str:
    bid = anahtar.split(":")[0]
    if bid.startswith("kvkk-karar-"):
        return KARAR_URL
    if bid.startswith("kanun-"):
        no = bid.split("-")[1]
        return f"https://www.mevzuat.gov.tr/mevzuat?MevzuatNo={no}&MevzuatTur=1&MevzuatTertip=5"
    return sources.get(bid, {}).get("sayfa_url") or sources.get(bid, {}).get("url") or ""


def yaz() -> None:
    sources = {v["belge_id"]: v for k, v in json.loads(Path("configs/sources.json").read_text(encoding="utf-8")).items()
               if not k.startswith("_")}
    L = ["# Değerlendirme seti doğrulama listesi", "",
         "Her soruda: resmî metni aç, beklenen kaynakta kanıt cümlesinin geçtiğini ve sorunun bu maddeyle cevaplandığını kontrol et.",
         "Doğruysa `[ ]` kutusunu `[x]` yap. Yanlış/eksikse `Not:` satırına yaz (ör. \"m.17 de beklenmeli\", \"soru belirsiz\").",
         "Kapsam dışı sorularda: derlemde (KVKK, İş Kanunu, İSG ve ilgili yönetmelik/tebliğler, seçili Kurul kararları) cevabı",
         "OLMADIĞINI kontrol et. Bitince: `python -m scripts.dogrulama_listesi --oku`", ""]
    for yol, baslik in SETLER:
        if not Path(yol).exists():
            continue
        qs = [json.loads(l) for l in open(yol, encoding="utf-8")]
        L += [f"## {baslik}", ""]
        for q in qs:
            L.append(f"### {q['id']} — {q['soru']}")
            if q["tur"] == "kapsam_disi":
                L.append("- Beklenen: **kapsam dışı** (sistem \"bilmiyorum\" demeli)")
            else:
                L.append("- Beklenen kaynak: " + ", ".join(
                    f"`{b}` ([resmî metin]({kaynak_url(b, sources)}))" for b in q["beklenen"]))
                if q.get("kanit"):
                    L.append(f"- Kanıt (derlemden): > {q['kanit'][:600].replace(chr(10), ' ')}")
                if q.get("anahtar"):
                    L.append("- Cevapta aranan: " + " VE ".join("(" + " | ".join(g) + ")" for g in q["anahtar"]))
            L += ["- [ ] Doğrulandı", "- Not: ", ""]
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print(f"{OUT} yazıldı")


def oku() -> None:
    t = OUT.read_text(encoding="utf-8")
    bloklar = re.split(r"\n### ", t)[1:]
    tamam, eksik, notlu = 0, [], []
    for b in bloklar:
        qid = b.split(" ", 1)[0]
        if "- [x] Doğrulandı" in b or "- [X] Doğrulandı" in b:
            tamam += 1
        else:
            eksik.append(qid)
        m = re.search(r"- Not: (.+)", b)
        if m and m.group(1).strip():
            notlu.append(f"{qid}: {m.group(1).strip()}")
    print(f"Doğrulanan: {tamam}/{len(bloklar)}")
    print("İşaretlenmemiş:", ", ".join(eksik) or "yok")
    print("Notlar:\n  " + "\n  ".join(notlu) if notlu else "Not yok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--oku", action="store_true")
    oku() if ap.parse_args().oku else yaz()
