"""Uçtan uca soru-cevap: iki kanallı arama -> eşik kontrolü -> LLM -> atıf doğrulama.

"Bilmiyorum" iki katmanlı (KARARLAR.md):
  1) Arama eşiği: dense top-1 benzerliği configs/answer.json'daki esik'in altındaysa LLM'e hiç gidilmez.
     Eşik eval setinden AYRI kalibrasyon setiyle belirlenir (eval/calibrate.py). Bu katman konudan
     uzak soruları yakalar.
  2) LLM: kaynaklar konuya yakın ama cevabı içermiyorsa model CEVAP_YOK döner.
Ayrıca cevapta hiç geçerli atıf yoksa cevap güvenilmez sayılır ve "bilmiyorum"a çevrilir.

Kullanım: python -m src.generate.answer "İşveren kamerayla ses kaydı alabilir mi?" --llm gemini
"""
from __future__ import annotations

import argparse
import json
import threading
import time
from collections.abc import Iterator
from pathlib import Path

from src.generate import prompt
from src.generate.llm import make_llm
from src.index.embed import Embedder
from src.retrieve.search import MEVZUAT_TURLERI, Searcher

CFG_PATH = Path("configs/answer.json")
DISCLAIMER = "Bu sistem hukuki tavsiye vermez; cevaplar yalnızca gösterilen kaynak metinlere dayanır."


def load_cfg() -> dict:
    return json.loads(CFG_PATH.read_text(encoding="utf-8")) if CFG_PATH.exists() else {}


def source_key(payload: dict) -> str:
    """Değerlendirmede kullanılan kaynak anahtarı: mevzuat 'belge_id:madde_no', karar 'kvkk-karar-YYYY-N'."""
    return payload["belge_id"] if payload["belge_tur"] == "karar" else f"{payload['belge_id']}:{payload['madde_no']}"


def source_entry(no: int, p: dict) -> dict:
    return {"no": no, "atif": p["atif"], "anahtar": source_key(p), "belge_tur": p["belge_tur"],
            "baslik": p.get("baslik"), "url": p.get("url"), "alinti": p["metin"][:300]}


def build_context(searcher: Searcher, query: str, esik: float | None) -> tuple[list, dict]:
    """Bağlamı kur: iki kanal ayrı aranır; dense top-1'i eşiğin altında kalan kanal bağlama girmez.

    Aynı kalibre eşik iki işte kullanılır: (a) iki kanal da eşiğin altındaysa soru kapsam dışı sayılır,
    (b) yalnız biri altındaysa o kanal atılır — aksi halde karar sorusuna ilgisiz kanun maddesi,
    mevzuat sorusuna ilgisiz karar karışıyor ve küçük modeller bunlardan gerekçe uyduruyordu.
    """
    m = searcher.search(query, "dense", top_k=1, belge_tur=MEVZUAT_TURLERI)
    k = searcher.search(query, "dense", top_k=1, belge_tur=["karar"])
    top = {"mevzuat": m[0].score if m else 0.0, "karar": k[0].score if k else 0.0}
    ctx = searcher.search_context(query, "hybrid")
    kanallar = [kn for kn in ("mevzuat", "karar") if esik is None or top[kn] >= esik]
    if not kanallar:  # eşik kapalıyken çağrılmaz; çağıran kapsam dışı kararını top1'den verir
        kanallar = [max(top, key=top.get)]
    hits = [h for kn in kanallar for h in ctx[kn]]
    return hits, {"dense_top1": round(max(top.values()), 4), "kanal_top1": {a: round(b, 4) for a, b in top.items()},
                  "kanallar": kanallar}


class Answerer:
    def __init__(self, llm_spec: str = "gemini", mode: str = "hibrit", embed_device: str | None = None):
        # Ollama ile çalışırken sorgu embedding'i CPU'da: 8 GB VRAM LLM'e kalsın (KARARLAR.md).
        if embed_device is None and llm_spec.startswith("ollama"):
            embed_device = "cpu"
        self.searcher = Searcher(mode, Embedder(device=embed_device))
        self.llm = make_llm(llm_spec)
        self.cfg = load_cfg()
        self._lock = threading.Lock()

    def prepare(self, query: str) -> tuple[dict | None, list, dict]:
        """Arama + eşik. Dönen: (erken "bilmiyorum" cevabı veya None, bağlam, ortak alanlar)."""
        t0 = time.time()
        esik = self.cfg.get("esik")
        with self._lock:  # embedding modeli ve sorgu önbelleği: aynı anda tek istek (API çok iş parçacıklı)
            hits, meta = build_context(self.searcher, query, esik)
        base = {"soru": query, "llm": self.llm.name, **meta, "esik": esik,
                "uyari": DISCLAIMER, "derlem_tarihi": self.cfg.get("derlem_tarihi"),
                "baglam": [h.payload["atif"] for h in hits], "baglam_anahtar": [source_key(h.payload) for h in hits],
                "arama_sn": round(time.time() - t0, 2)}
        if esik is not None and meta["dense_top1"] < esik:
            return ({**base, "bilmiyorum": True, "bilmiyorum_katmani": "arama_esigi", "cevap": prompt.NO_ANSWER_TEXT,
                     "neden": "Soru, derlemdeki kaynaklara yeterince yakın değil.", "kaynaklar": [],
                     "gecersiz_atif": [], "sure_sn": round(time.time() - t0, 2)}, hits, base)
        return None, hits, base

    def finalize(self, raw: str, hits: list, base: dict, llm_sn: float) -> dict:
        """LLM çıktısı -> doğrulanmış cevap (CEVAP_YOK, atıf doğrulama, kaynak listesi)."""
        parsed = prompt.parse_answer(raw, len(hits))
        katman = "llm" if parsed["bilmiyorum"] else None
        if parsed["bilmiyorum"]:
            # Modelin kendi gerekçesi gösterilmez: kaynak göstermeden yazıldığı için uydurma içerebiliyor
            # (qwen2.5 "son asgari ücret tespiti 2018" diye uydurdu). Ham metin "ham" alanında kalır.
            parsed["neden"] = "Bulunan kaynaklar bu soruyu cevaplamaya yetmiyor."
        if not parsed["bilmiyorum"] and not parsed["atif_no"]:
            parsed.update(bilmiyorum=True, cevap=prompt.NO_ANSWER_TEXT, neden="Model kaynak göstermeden cevap verdi; cevap atıldı.")
            katman = "atif_dogrulama"
        kaynaklar = [source_entry(n, hits[n - 1].payload) for n in parsed["atif_no"]]
        return {**base, "bilmiyorum": parsed["bilmiyorum"], "bilmiyorum_katmani": katman, "cevap": parsed["cevap"],
                "neden": parsed["neden"], "kaynaklar": kaynaklar, "gecersiz_atif": parsed["gecersiz_atif"],
                "ham": raw, "sure_sn": round(base["arama_sn"] + llm_sn, 2), "llm_sn": round(llm_sn, 2)}

    def answer(self, query: str) -> dict:
        early, hits, base = self.prepare(query)
        if early:
            return early
        t1 = time.time()
        raw = self.llm.generate(prompt.SYSTEM, prompt.build_user(query, hits))
        return self.finalize(raw, hits, base, time.time() - t1)

    def answer_stream(self, query: str) -> Iterator[tuple[str, dict]]:
        """Akışlı cevap: ("baglam", {...}) -> ("parca", {"metin": ...})* -> ("sonuc", doğrulanmış cevap).

        Doğrulama akıştan SONRA da yapılır ve "sonuc" olayı esas alınır: hiç geçerli atıf yoksa akıtılan
        metin atılır, istemci "bilmiyorum" gösterir. CEVAP_YOK ile başlayan çıktı hiç akıtılmaz.
        """
        early, hits, base = self.prepare(query)
        if early:
            yield "sonuc", early
            return
        yield "baglam", {"kaynaklar": [source_entry(i, h.payload) for i, h in enumerate(hits, 1)]}
        t1 = time.time()
        buf, sent = "", 0
        for delta in self.llm.stream(prompt.SYSTEM, prompt.build_user(query, hits)):
            buf += delta
            head = buf.lstrip().upper()
            if head.startswith(prompt.NO_ANSWER) or prompt.NO_ANSWER.startswith(head):
                continue  # "bilmiyorum" (veya henüz belli değil): modelin gerekçesi kullanıcıya akıtılmaz
            yield "parca", {"metin": buf[sent:]}
            sent = len(buf)
        yield "sonuc", self.finalize(buf, hits, base, time.time() - t1)


def render(a: dict) -> str:
    lines = [a["cevap"]]
    if a["bilmiyorum"] and a.get("neden"):
        lines.append(f"({a['neden']})")
    if a["kaynaklar"]:
        lines.append("\nKaynaklar:")
        lines += [f"  [{k['no']}] {k['atif']}" + (f" — {k['url']}" if k.get("url") else "") for k in a["kaynaklar"]]
    if a.get("derlem_tarihi"):
        lines.append(f"\nKaynak metinlerin son kontrol tarihi: {a['derlem_tarihi']}")
    lines.append(a["uyari"])
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--llm", default="gemini")
    args = ap.parse_args()
    a = Answerer(args.llm).answer(args.query)
    print(render(a))
    print(f"\n[{a['llm']} | dense_top1={a['dense_top1']} | {a['sure_sn']} sn]")


if __name__ == "__main__":
    main()
