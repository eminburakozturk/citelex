"""Yerel LLM seçimi: aynı 5 soru, aynı bağlam, farklı modeller (+ referans olarak Gemini).

Sorular eval setinden DEĞİL (arama sağlık seti ve kalibrasyon setinden); eval seti model seçiminde
kullanılmaz. Soru düzeyindeki arama eşiği bu karşılaştırmada KAPALI (kanal eşiği açık): amaç modelin kendi davranışını (kaynak gösterme,
CEVAP_YOK'a uyma, Türkçe) görmek. Bağlam bir kez üretilir, tüm modellere aynısı verilir.

Ölçülen (otomatik): geçerli/geçersiz atıf sayısı, CEVAP_YOK'a uyum (kapsam dışı soruda), süre.
Cevabın içerik doğruluğu otomatik ölçülmez; cevap metinleri rapora yazılır ve elle okunur.

Kullanım: python -m eval.compare_llm --llm ollama:qwen2.5:7b ollama:qwen3:8b gemini
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from src.generate import prompt
from src.generate.answer import build_context, load_cfg
from src.generate.llm import make_llm
from src.index.embed import Embedder
from src.retrieve.search import Searcher

QUESTIONS = [  # (id, soru, cevap bekleniyor mu)
    ("c01", "İşçi iş sözleşmesini feshederken ne kadar önceden haber vermeli?", True),
    ("c02", "Gece çalışması en fazla kaç saat sürebilir?", True),
    ("k01", "İşveren işyerindeki güvenlik kamerasıyla ses kaydı alabilir mi?", True),
    ("k03", "Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyebilir mi?", True),
    ("r10", "2026 yılında net asgari ücret ne kadardır?", False),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", nargs="+", default=["ollama:qwen2.5:7b", "ollama:qwen3:8b", "gemini"])
    ap.add_argument("--out", default="results/llm_compare.md")
    args = ap.parse_args()

    s = Searcher("hibrit", Embedder(device="cpu"))  # yerel LLM senaryosu: embedding CPU'da
    ctxs = {}
    esik = load_cfg().get("esik")
    for qid, q, _ in QUESTIONS:
        ctxs[qid], _ = build_context(s, q, esik)  # kanal eşiği açık; soru düzeyinde ret kapalı

    lines = ["# LLM karşılaştırması (5 soru, aynı bağlam)", "",
             "Sorular eval setinden değil. Arama eşiği kapalı. İçerik doğruluğu elle okunmalı; tablo yalnızca otomatik ölçülenleri verir.", ""]
    summary = []
    detail = []
    for spec in args.llm:
        llm = make_llm(spec)
        tot_t, ok_cite, bad_cite, no_cite, noans_ok, errs = 0.0, 0, 0, 0, None, 0
        for qid, q, expect in QUESTIONS:
            hits = ctxs[qid]
            t = time.time()
            try:
                raw = llm.generate(prompt.SYSTEM, prompt.build_user(q, hits))
            except Exception as e:  # noqa: BLE001
                raw = f"HATA: {type(e).__name__}: {str(e)[:150]}"
                errs += 1
            dt = time.time() - t
            tot_t += dt
            p = prompt.parse_answer(raw, len(hits))
            ok_cite += len(p["atif_no"])
            bad_cite += len(p["gecersiz_atif"])
            if expect and not p["bilmiyorum"] and not p["atif_no"]:
                no_cite += 1
            if not expect:
                noans_ok = p["bilmiyorum"]
            atiflar = "; ".join(hits[n - 1].payload["atif"] for n in p["atif_no"])
            detail += [f"### {spec} — {qid}: {q}", "", f"_{dt:.1f} sn | atıflar: {atiflar or '—'} | geçersiz: {p['gecersiz_atif']}_", "",
                       "> " + raw.replace("\n", "\n> "), ""]
            print(f"{spec} {qid} {dt:.1f}sn bilmiyorum={p['bilmiyorum']} atif={p['atif_no']} gecersiz={p['gecersiz_atif']}", flush=True)
        summary.append(f"| {spec} | {tot_t / len(QUESTIONS):.1f} | {ok_cite} | {bad_cite} | {no_cite} | "
                       f"{'evet' if noans_ok else 'HAYIR'} | {errs} |")
    lines += ["| Model | Ort. süre (sn) | Geçerli atıf | Geçersiz atıf | Atıfsız cevap | Kapsam dışında CEVAP_YOK | Hata |",
              "|---|---|---|---|---|---|---|"] + summary + ["", "## Cevaplar", ""] + detail
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines[4:6] + summary))


if __name__ == "__main__":
    main()
