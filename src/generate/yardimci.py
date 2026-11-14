"""Kaynak paneli ve cevap altı yardımcıları (LLM): madde açıklaması ve ilgili sorular.

- aciklama(): bir maddeyi sade Türkçeyle 2-4 madde işaretiyle ve isteğe bağlı bir örnekle açıklar. Girdi YALNIZ o maddenin
  metnidir; talimat kaynağın dışına çıkmayı ve hukuki tavsiyeyi yasaklar. Sonuç anahtara göre önbellekte tutulur
  (aynı madde ikinci kez LLM'e gitmez).
- ilgili_sorular(): cevaptan sonra 5 aday takip sorusu üretir, yalnız derlemde cevabı olabilecekleri (dense top1 >= eşik)
  döndürür (en çok 3) — sistemin "bilmiyorum" diyeceği soru önerilmez.
Her ikisi de kullanıcı tıkladığında çağrılır; API'de /sor ile aynı istek sınırına tabidir.
"""
from __future__ import annotations

import json
import re
import threading
from collections import OrderedDict

ACIKLAMA_SYSTEM = """Sen bir mevzuat metnini sade Türkçeyle açıklayan yardımcısın.
YALNIZ verilen madde metnine dayan; metinde olmayan bilgi, yorum, içtihat veya tavsiye ekleme. Hukuki tavsiye verme.
Günlük dille 2-4 kısa madde yaz. Metin uygunsa somut bir örnek ver; örnekteki sayılar metindeki sayılardan çıkmalı.
Türkçe karakterleri (ç, ğ, ı, İ, ö, ş, ü) doğru kullan; yazım ve dil bilgisi hatası yapma.
YALNIZ şu JSON'u döndür: {"maddeler": ["...", "..."], "ornek": "..." veya null}"""

ILGILI_SYSTEM = """Kullanıcı Türk mevzuatı hakkında bir soru sordu ve cevap aldı. Aynı konuda kullanıcının sorabileceği
5 KISA takip sorusu yaz (her biri en çok 90 karakter, Türkçe, soru işaretiyle biten, birbirinden farklı).
Verilen kaynak başlıklarının kapsamında kal. Türkçe karakterleri (ç, ğ, ı, İ, ö, ş, ü) doğru kullan; yazım ve dil bilgisi hatası yapma. YALNIZ şu JSON'u döndür: {"sorular": ["...", "..."]}"""

ACIKLAMA_UYARI = "Yapay zekâ açıklaması; yalnızca bu maddenin metnine dayanır. Hukuki tavsiye değildir, resmî metni esas alın."


class _LRU:
    def __init__(self, n: int = 256):
        self.n, self.d, self.lock = n, OrderedDict(), threading.Lock()

    def get(self, k):
        with self.lock:
            if k in self.d:
                self.d.move_to_end(k)
                return self.d[k]
        return None

    def put(self, k, v):
        with self.lock:
            self.d[k] = v
            self.d.move_to_end(k)
            while len(self.d) > self.n:
                self.d.popitem(last=False)


_aciklama_cache = _LRU()
_ilgili_cache = _LRU()


def _json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("JSON yok")
    return json.loads(m.group(0))


def aciklama(llm, madde: dict) -> dict:
    """madde: src.tools.madde_getir çıktısı."""
    key = madde["anahtar"]
    hit = _aciklama_cache.get(key)
    if hit:
        return hit
    metin = "\n".join((f"({p['fikra_no']}) " if p.get("fikra_no") else "") + p["metin"]
                      for p in madde["parcalar"] if not p.get("mulga"))[:8000]
    user = f"MADDE: {madde['atif']} — {madde.get('baslik') or ''}\n\nMETİN:\n{metin}"
    j = _json(llm.generate(ACIKLAMA_SYSTEM, user, max_tokens=600))
    maddeler = [str(x).strip() for x in j.get("maddeler", []) if str(x).strip()][:4]
    if not maddeler:
        raise ValueError("açıklama boş")
    out = {"anahtar": key, "atif": madde["atif"], "maddeler": maddeler,
           "ornek": (str(j["ornek"]).strip() or None) if j.get("ornek") else None, "uyari": ACIKLAMA_UYARI}
    _aciklama_cache.put(key, out)
    return out


def ilgili_sorular(llm, searcher, soru: str, basliklar: list[str], esik: float | None, n: int = 3) -> list[str]:
    key = (soru.strip().lower(), tuple(basliklar))
    hit = _ilgili_cache.get(key)
    if hit is not None:
        return hit
    user = f"SORU: {soru}\nKAYNAKLAR: " + "; ".join(basliklar[:6])
    adaylar = [str(s).strip() for s in _json(llm.generate(ILGILI_SYSTEM, user, max_tokens=300)).get("sorular", [])]
    adaylar = [s for s in adaylar if 8 <= len(s) <= 120 and s.lower() != soru.strip().lower()]
    out = []
    for s in adaylar:
        if esik is not None:
            m = searcher.search(s, "dense", top_k=1, belge_tur=["kanun", "yonetmelik", "teblig"])
            k = searcher.search(s, "dense", top_k=1, belge_tur=["karar"])
            if max([h.score for h in m + k] or [0.0]) < esik:
                continue   # derlemde cevabı olmayacak soru önerilmez
        out.append(s)
        if len(out) >= n:
            break
    _ilgili_cache.put(key, out)
    return out
