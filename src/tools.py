"""Ortak araç katmanı: aynı iki araç üç yerden sunulur — API (/kaynak), MCP sunucusu (src/mcp_server.py) ve
LangGraph ajan modu (18 Kas). Tek kez yazılır; davranış her yerde aynıdır.

  mevzuat_ara(soru, turler, k)  -> numaralı kaynak listesi (iki kanallı hibrit arama + bağlam kurma; atıf anahtarlarıyla)
  madde_getir(anahtar)          -> bir maddenin/kararın tam metni ('belge_id:madde_no' | 'kvkk-karar-YYYY-N')

Araçlar LLM çağırmaz; cevap üretimi (ve atıf doğrulama) çağıranın işidir.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from src.generate.answer import build_context, source_key

RE_ANAHTAR = re.compile(r"^[a-z0-9-]{2,60}(:[0-9A-Za-zÇĞİÖŞÜçğıöşü /]{1,20})?$")
TURLER = ("kanun", "yonetmelik", "teblig", "karar")
SOURCES_PATH = Path("configs/sources.json")


class AracHatasi(ValueError):
    """Geçersiz girdi veya bulunamayan kaynak (status: 400 | 404)."""

    def __init__(self, msg: str, status: int = 400):
        super().__init__(msg)
        self.status = status


def _sources() -> dict:
    if not SOURCES_PATH.exists():
        return {}
    return {v["belge_id"]: v for k, v in json.loads(SOURCES_PATH.read_text(encoding="utf-8")).items()
            if not k.startswith("_")}


def mevzuat_ara(searcher, soru: str, turler: list[str] | None = None, k: int = 5,
                esik: float | None = None, max_metin: int = 1500) -> dict:
    """Soru için kaynak ara. esik verilirse dense benzerliği altındaki kanallar atılır (Answerer ile aynı kural)."""
    soru = (soru or "").strip()
    if not 3 <= len(soru) <= 500:
        raise AracHatasi("Soru 3-500 karakter olmalı.")
    if turler is not None:
        bad = [t for t in turler if t not in TURLER]
        if bad or not turler:
            raise AracHatasi(f"Geçersiz tür: {bad or 'boş'}; izin verilen: {', '.join(TURLER)}")
    hits, meta = build_context(searcher, soru, esik, turler)
    if esik is not None and meta["dense_top1"] < esik:
        return {"soru": soru, "kapsam_disi": True, "kaynaklar": [],
                "not": "Soru derlemdeki kaynaklara yeterince yakın değil."}
    return {"soru": soru, "kapsam_disi": False, "kanallar": meta["kanallar"],
            "kaynaklar": [{"no": i, "anahtar": source_key(h.payload), "atif": h.payload["atif"],
                           "belge_tur": h.payload["belge_tur"], "baslik": h.payload.get("baslik"),
                           "metin": h.payload["metin"][:max_metin]} for i, h in enumerate(hits[:k * 2], 1)]}


def madde_getir(searcher, anahtar: str, son_kontrol: str | None = None) -> dict:
    """Atıf anahtarından madde/karar metni (API /kaynak ile aynı çıktı)."""
    if not RE_ANAHTAR.match(anahtar or ""):
        raise AracHatasi("Geçersiz kaynak anahtarı.")
    from qdrant_client import models
    bid, _, mno = anahtar.partition(":")
    must = [models.FieldCondition(key="belge_id", match=models.MatchValue(value=bid))]
    if mno:
        must.append(models.FieldCondition(key="madde_no", match=models.MatchValue(value=mno)))
    pts, _ = searcher.client.scroll(searcher.name, scroll_filter=models.Filter(must=must), limit=100, with_payload=True)
    genis = getattr(searcher, "genis", None)
    if not pts and genis is not None and bid.startswith("kanun-"):   # geniş katman atfı ("kanun-6098:342")
        pts, _ = genis.client.scroll(genis.name, scroll_filter=models.Filter(must=must), limit=200, with_payload=True)
    ps = [p.payload for p in pts]
    if not ps or (not mno and ps[0]["belge_tur"] != "karar"):
        raise AracHatasi("Kaynak bulunamadı.", 404)
    ilk = ps[0]
    if ilk["belge_tur"] == "karar":
        sira = {"sikayet": 0, "savunma": 1, "degerlendirme": 2, "hukum": 3}
        ps.sort(key=lambda p: (sira.get(p.get("bolum"), 9), int(p["chunk_id"].rsplit("-", 1)[-1])))
        atif, url = f"KVKK Kurulu K. {ilk['belge_no']}", ilk.get("url")
    else:
        ps.sort(key=lambda p: (p.get("fikra_no") or 0, p.get("parca_no") or 0))
        for p in ps:   # bölünmüş uzun fıkra: giriş cümlesi yalnız ilk parçada gösterilir
            if (p.get("parca_no") or 1) > 1 and p.get("giris") and p["metin"].startswith(p["giris"]):
                p["metin"] = p["metin"][len(p["giris"]):].lstrip("\n")
        atif = re.sub(r"/\d+$", "", ilk["atif"]) if ilk.get("fikra_no") is not None else ilk["atif"]
        url = _sources().get(bid, {}).get("sayfa_url")
    return {"anahtar": anahtar, "atif": atif, "belge_tur": ilk["belge_tur"], "belge_adi": ilk["belge_adi"],
            "baslik": ilk.get("baslik"), "url": url, "karar_tarihi": ilk.get("karar_tarihi"),
            "mulga": all(p.get("mulga") for p in ps), "son_kontrol": son_kontrol,
            "parcalar": [{"fikra_no": p.get("fikra_no"), "bolum": p.get("bolum") if ilk["belge_tur"] == "karar" else None,
                          "metin": p["metin"], "mulga": bool(p.get("mulga"))} for p in ps],
            "dipnotlar": ilk.get("dipnotlar") or []}
