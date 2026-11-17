"""Uçtan uca değerlendirme: eval/questions.jsonl -> results/eval_<llm>.md (+ .jsonl ham cevaplar).

Kapsam içi sorularda (her biri 0/1):
  baglam   : beklenen kaynak LLM'e verilen bağlamda mı            (arama + bağlam kurma)
  atif     : cevap beklenen kaynağa atıf yapıyor mu               (kaynak gösterme)
  icerik   : cevap metni tüm anahtar gruplarını içeriyor mu       (cevap içeriği; anahtar kelime eşleşmesi)
  dogru    : cevap verdi VE atif VE icerik                        (sıkı ölçüt)
  yanlis_ret: cevabı derlemde olduğu halde "bilmiyorum" dedi (hangi katmanda: eşik / LLM / atıf doğrulama)
Kapsam dışı sorularda:
  dogru_ret: "bilmiyorum" dedi (hangi katmanda); aksi halde uydurma cevap.

SINIRLAR (README'de de yazılmalı):
  - icerik anahtar kelime eşleşmesidir: doğru kelimeyi yanlış bağlamda yazan cevap geçer, doğru cevabı
    farklı kelimeyle yazan cevap kalır. Ham cevaplar .jsonl'de; şüpheli olanlar elle okunmalı.
  - Beklenen cevaplar resmî metinle elle doğrulandı (eval/DOGRULAMA.md, 74/74); eval/validate_questions.py ayrıca yalnız derlemdeki metne dayandığını doğrular);
    kullanıcı doğrulaması bekliyor.
  - Eşik ve prompt bu set üzerinde AYARLANMAZ (kalibrasyon ayrı sette).

Her çalıştırma results/eval_history.jsonl'e bir özet satırı ekler (15 Kas: güncelleme sonrası regresyon).

Kullanım: python -m eval.run_eval --llm ollama:qwen2.5:7b [--limit 10]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from src.generate.answer import Answerer
from src.index.tokenize import turkish_lower


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", turkish_lower(s))


def score(q: dict, a: dict) -> dict:
    if q["tur"] == "kapsam_disi":
        return {"dogru_ret": a["bilmiyorum"], "katman": a.get("bilmiyorum_katmani")}
    bek = set(q["beklenen"])
    baglam = bool(bek & set(a.get("baglam_anahtar", [])))
    atif = bool(bek & {k["anahtar"] for k in a.get("kaynaklar", [])})
    cevap = norm(a["cevap"]) if not a["bilmiyorum"] else ""
    icerik = bool(cevap) and all(any(norm(alt) in cevap for alt in grp) for grp in q["anahtar"])
    return {"baglam": baglam, "atif": atif, "icerik": icerik, "dogru": (not a["bilmiyorum"]) and atif and icerik,
            "yanlis_ret": a["bilmiyorum"], "katman": a.get("bilmiyorum_katmani")}


def pct(x: int, n: int) -> str:
    return f"{x}/{n} (%{100 * x / n:.0f})" if n else "—"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", default="ollama:qwen2.5:7b")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--ajan", action="store_true", help="LangGraph ajan modu (src/agent.py)")
    ap.add_argument("--sadece", default=None, help="virgüllü soru id'leri")
    args = ap.parse_args()

    qs = [json.loads(l) for l in open("eval/questions.jsonl", encoding="utf-8")][: args.limit]
    if args.sadece:
        ids = set(args.sadece.split(","))
        qs = [q for q in qs if q["id"] in ids]
    ans = Answerer(args.llm)
    if args.ajan:
        from src.agent import AgentAnswerer
        ans = AgentAnswerer(ans)
    tag = re.sub(r"[^a-z0-9.]+", "_", args.llm.lower()) + ("_rerank" if ans.searcher.rerank else "") + ("_ajan" if args.ajan else "") + ("_genis" if getattr(ans.searcher, "genis", None) is not None else "") + ("_kismi" if args.sadece else "")
    raw_path = Path(f"results/eval_{tag}.jsonl")
    rows, errors, ardisik = [], 0, 0
    with raw_path.open("w", encoding="utf-8", newline="\n") as fh:
        for i, q in enumerate(qs, 1):
            t = time.time()
            try:
                a = ans.answer(q["soru"])
            except Exception as e:  # noqa: BLE001 — tek sorunun hatası değerlendirmeyi durdurmasın
                errors += 1
                ardisik += 1
                print(f"[{i}/{len(qs)}] {q['id']} HATA {type(e).__name__}: {str(e)[:160]}", flush=True)
                fh.write(json.dumps({"id": q["id"], "hata": f"{type(e).__name__}: {str(e)[:200]}"}, ensure_ascii=False) + "\n")
                if ardisik >= 3:  # altyapı sorunu (Qdrant/LLM kapalı): sahte sonuç üretme, dur
                    raise SystemExit("Art arda 3 hata: altyapı sorunu. Değerlendirme durduruldu, rapor yazılmadı.") from e
                continue  # hatalı soru metriklere GİRMEZ (ne doğru ne yanlış sayılır)
            ardisik = 0
            a["sure_sn"] = round(time.time() - t, 2)
            s = score(q, a)
            rows.append((q, a, s))
            fh.write(json.dumps({"id": q["id"], "tur": q["tur"], "soru": q["soru"], "beklenen": q["beklenen"],
                                 "skor": s, "cevap": a["cevap"], "kaynaklar": [k["atif"] for k in a.get("kaynaklar", [])],
                                 "baglam_anahtar": a.get("baglam_anahtar"), "dense_top1": a.get("dense_top1"),
                                 "gecersiz_atif": a.get("gecersiz_atif"), "sure_sn": a["sure_sn"],
                                 "ajan_sorgular": a.get("ajan_sorgular"),
                                 "hata": a.get("hata")}, ensure_ascii=False) + "\n")
            print(f"[{i}/{len(qs)}] {q['id']} {s} {a['sure_sn']}sn", flush=True)

    ic = [(q, a, s) for q, a, s in rows if q["tur"] != "kapsam_disi"]
    dis = [(q, a, s) for q, a, s in rows if q["tur"] == "kapsam_disi"]
    by = defaultdict(list)
    for q, a, s in ic:
        by["karar" if q["tur"] == "karar" else "mevzuat"].append(s)
    tot = {k: sum(s[k] for _, _, s in ic) for k in ("baglam", "atif", "icerik", "dogru", "yanlis_ret")}
    ret_katman = defaultdict(int)
    for _, _, s in ic:
        if s["yanlis_ret"]:
            ret_katman[s["katman"]] += 1
    dis_ok = sum(s["dogru_ret"] for _, _, s in dis)
    dis_katman = defaultdict(int)
    for _, _, s in dis:
        if s["dogru_ret"]:
            dis_katman[s["katman"]] += 1
    gecersiz = sum(len(a.get("gecersiz_atif") or []) for _, a, _ in rows)
    sure = sorted(a["sure_sn"] for _, a, _ in rows)
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception:  # noqa: BLE001
        commit = "?"

    L = [f"# Değerlendirme — {ans.llm.name}", "",
         f"Tarih: {datetime.now():%Y-%m-%d %H:%M} | commit: {commit} | eşik: {ans.cfg.get('esik')} | reranker: {'açık' if ans.searcher.rerank else 'kapalı'} | soru: {len(rows)} "
         f"({len(ic)} kapsam içi, {len(dis)} kapsam dışı) | hata: {errors}", "",
         "Beklenen cevaplar resmî metinle elle doğrulandı (74/74; geliştirici kontrolü, hukukçu incelemesi değildir). `icerik` anahtar kelime eşleşmesidir; "
         "kesin doğruluk için ham cevaplar elle okunmalı.", "",
         "## Kapsam içi", "", "| Ölçüt | Tümü | Mevzuat | Karar |", "|---|---|---|---|"]
    for k, ad in [("baglam", "Beklenen kaynak bağlamda"), ("atif", "Beklenen kaynağa atıf"), ("icerik", "Cevap içeriği (anahtar)"),
                  ("dogru", "**Doğru (cevap + atıf + içerik)**"), ("yanlis_ret", "Yanlış \"bilmiyorum\"")]:
        L.append(f"| {ad} | {pct(tot[k], len(ic))} | {pct(sum(s[k] for s in by['mevzuat']), len(by['mevzuat']))} | "
                 f"{pct(sum(s[k] for s in by['karar']), len(by['karar']))} |")
    L += ["", f"Yanlış \"bilmiyorum\" katmanları: {dict(ret_katman) or '—'}", "",
          "## Kapsam dışı", "",
          f"Doğru \"bilmiyorum\": {pct(dis_ok, len(dis))} — katmanlar: {dict(dis_katman) or '—'}", "",
          "## Diğer", "",
          f"Geçersiz atıf (bağlamda olmayan [n]): {gecersiz} | süre medyan {sure[len(sure) // 2]} sn, en uzun {sure[-1]} sn", "",
          "## Başarısız sorular", "", "| # | Soru | Bağlam | Atıf | İçerik | Not |", "|---|---|---|---|---|---|"]
    for q, a, s in ic:
        if not s["dogru"]:
            notu = f"bilmiyorum ({s['katman']})" if s["yanlis_ret"] else a["cevap"][:110].replace("\n", " ").replace("|", "/")
            L.append(f"| {q['id']} | {q['soru']} | {'✓' if s['baglam'] else '✗'} | {'✓' if s['atif'] else '✗'} | "
                     f"{'✓' if s['icerik'] else '✗'} | {notu} |")
    for q, a, s in dis:
        if not s["dogru_ret"]:
            L.append(f"| {q['id']} | {q['soru']} | — | — | — | CEVAP VERDİ: {a['cevap'][:110].replace(chr(10), ' ').replace('|', '/')} |")
    Path(f"results/eval_{tag}.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    with open("results/eval_history.jsonl", "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"tarih": f"{datetime.now():%Y-%m-%dT%H:%M}", "llm": ans.llm.name, "commit": commit,
                             "n_ic": len(ic), "n_dis": len(dis), **tot, "dogru_ret": dis_ok, "gecersiz_atif": gecersiz,
                             "hata": errors, "tam": args.limit is None and not args.sadece and errors == 0, "ajan": args.ajan,
                             "rerank": ans.searcher.rerank, "genis": getattr(ans.searcher, "genis", None) is not None}, ensure_ascii=False) + "\n")
    print("\n".join(L[:22]))


if __name__ == "__main__":
    main()
