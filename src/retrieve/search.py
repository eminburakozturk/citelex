"""Arama: dense, bm25 veya hibrit (RRF, k=60).

Varsayılan filtre (iki alt aramaya da uygulanır): mulga=false VE diger_kanuna_islendi=false.
Opsiyonel: belge_tur (kanun/yonetmelik/teblig) filtresi.

Kullanım: python -m src.retrieve.search "yıllık izin kaç gün" --mode hibrit --method hybrid
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass

from qdrant_client import QdrantClient, models

from src.index import bm25
from src.index.build import QDRANT_URL, collection_name
from src.index.embed import Embedder

RRF_K = 60
PREFETCH = 50
MEVZUAT_TURLERI = ["kanun", "yonetmelik", "teblig"]
MAX_MADDE_CHARS = 3000  # bağlama tam madde girer; daha uzunsa eşleşen fıkra + komşuları


def build_filter(belge_tur: list[str] | None = None, include_inactive: bool = False) -> models.Filter | None:
    must: list[models.Condition] = []
    if not include_inactive:
        must += [
            models.FieldCondition(key="mulga", match=models.MatchValue(value=False)),
            models.FieldCondition(key="diger_kanuna_islendi", match=models.MatchValue(value=False)),
        ]
    if belge_tur:
        must.append(models.FieldCondition(key="belge_tur", match=models.MatchAny(any=belge_tur)))
    return models.Filter(must=must) if must else None


@dataclass
class Hit:
    score: float
    payload: dict


class Searcher:
    def __init__(self, mode: str = "hibrit", embedder: Embedder | None = None):
        self.client = QdrantClient(url=QDRANT_URL)
        self.name = collection_name(mode)
        self.embedder = embedder or Embedder()
        self._qcache: dict[str, list[float]] = {}

    def search(self, query: str, method: str = "hybrid", top_k: int = 10,
               belge_tur: list[str] | None = None, include_inactive: bool = False) -> list[Hit]:
        flt = build_filter(belge_tur, include_inactive)
        idx, val = bm25.query_vector(query)
        sparse = models.SparseVector(indices=idx, values=val)
        if method == "bm25":
            res = self.client.query_points(self.name, query=sparse, using="bm25",
                                           query_filter=flt, limit=top_k, with_payload=True)
        else:
            if query not in self._qcache:  # aynı soru iki kanalda/yöntemde tekrar embed edilmesin
                if len(self._qcache) >= 256:  # uzun yaşayan API sürecinde sınırsız büyümesin
                    self._qcache.clear()
                self._qcache[query] = self.embedder.embed_query(query).tolist()
            dense = self._qcache[query]
            if method == "dense":
                res = self.client.query_points(self.name, query=dense, using="dense",
                                               query_filter=flt, limit=top_k, with_payload=True)
            elif method == "hybrid":
                res = self.client.query_points(
                    self.name,
                    prefetch=[
                        models.Prefetch(query=dense, using="dense", filter=flt, limit=PREFETCH),
                        models.Prefetch(query=sparse, using="bm25", filter=flt, limit=PREFETCH),
                    ],
                    query=models.RrfQuery(rrf=models.Rrf(k=RRF_K)),
                    limit=top_k, with_payload=True,
                )
            else:
                raise ValueError(method)
        return [Hit(p.score, p.payload) for p in res.points]

    def expand_to_articles(self, hits: list[Hit], k: int) -> list[Hit]:
        """Fıkra üzerinden ara, maddenin tamamını ver ("small-to-big").

        Arama birimi fıkra (isabetli eşleşme), bağlam birimi madde: eşleşen fıkranın kardeş fıkraları
        da bağlama girer. Aksi halde tanım fıkrası bulunup asıl hükmü taşıyan fıkra dışarıda kalıyordu
        (4857 m.69: "gece" tanımı 69/1 bulundu, 7,5 saat sınırı 69/3 bağlama girmedi).
        Madde MAX_MADDE_CHARS'ı aşıyorsa yalnız eşleşen fıkralar ve birer komşuları alınır.
        Sonuç: sıralaması korunmuş en çok k FARKLI madde; atıf madde düzeyinde.
        """
        groups: dict[tuple, list[Hit]] = {}
        for h in hits:
            p = h.payload
            groups.setdefault((p["belge_id"], p["madde_tur"], p["madde_no"]), []).append(h)
        out: list[Hit] = []
        for (bid, mtur, mno), grp in list(groups.items())[:k]:
            first = grp[0]
            if first.payload.get("fikra_no") is None and first.payload.get("parca_no") is None:  # madde tek parça
                out.append(first)
                continue
            pts, _ = self.client.scroll(self.name, scroll_filter=models.Filter(must=[
                models.FieldCondition(key="belge_id", match=models.MatchValue(value=bid)),
                models.FieldCondition(key="madde_tur", match=models.MatchValue(value=mtur)),
                models.FieldCondition(key="madde_no", match=models.MatchValue(value=mno)),
                models.FieldCondition(key="mulga", match=models.MatchValue(value=False)),
            ]), limit=200, with_payload=True)
            fk = sorted((p.payload for p in pts), key=lambda x: (x.get("fikra_no") or 0, x.get("parca_no") or 0))
            eslesen = sorted({h.payload["fikra_no"] for h in grp if h.payload.get("fikra_no") is not None})
            eslesen_id = {h.payload["chunk_id"] for h in grp}
            if sum(len(x["metin"]) for x in fk) > MAX_MADDE_CHARS:
                # Bölünmemiş fıkralar: eşleşen ± 1. Bölünmüş uzun fıkra (tanımlar, bent listesi): yalnız eşleşen parçalar.
                keep = {n + d for n in eslesen for d in (-1, 0, 1)}
                fk = [x for x in fk if x["chunk_id"] in eslesen_id
                      or (x.get("parca_no") is None and x.get("fikra_no") in keep)]
            satirlar, onceki = [], None
            for x in fk:
                metin = x["metin"]
                if x.get("parca_no") is not None:
                    ayni = onceki is not None and onceki.get("fikra_no") == x.get("fikra_no") and onceki.get("parca_no") is not None
                    if ayni and x.get("giris") and x["giris"] == onceki.get("giris"):
                        metin = metin[len(x["giris"]):].lstrip("\n")   # aynı giriş cümlesini tekrar etme
                etiket = (f"{x['fikra_no']}. fıkra" if x.get("fikra_no") is not None else "") + \
                         (" (ilgili bentler)" if x.get("parca_no") is not None else "")
                satirlar.append(f"{etiket.strip()}: {metin}" if etiket.strip() else metin)
                onceki = x
            payload = dict(first.payload)
            payload.update(
                fikra_no=None, parca_no=None, eslesen_fikralar=eslesen,
                atif=re.sub(r"/\d+$", "", first.payload["atif"]),
                metin="\n".join(satirlar),
            )
            out.append(Hit(first.score, payload))
        return out

    def search_context(self, query: str, method: str = "hybrid", k_mevzuat: int = 5,
                       k_karar: int = 3, per_karar: int = 2, max_chars: int | None = 14000,
                       mevzuat_tur: list[str] | None = None) -> dict[str, list[Hit]]:
        """İki kanallı arama: mevzuat ve karar AYRI aranır (KARARLAR.md 2026-11-12).

        Tek havuzda kararlar, alıntıladıkları kanun maddesini ilk 5'in dışına itiyordu ve ilk
        sonuçların hepsi aynı karardan geliyordu. Burada birincil kaynak (mevzuat) için k_mevzuat
        yer ayrılır; karar kanalında en çok k_karar farklı karar, karar başına per_karar parça alınır.
        """
        mevzuat = self.expand_to_articles(
            self.search(query, method, top_k=k_mevzuat * 3, belge_tur=mevzuat_tur or MEVZUAT_TURLERI), k_mevzuat)
        aday = self.search(query, method, top_k=30, belge_tur=["karar"])
        # 1) Kararı OLGULARDAN bul: herhangi bir bölümü eşleşen ilk k_karar farklı karar.
        sira: list[str] = list(dict.fromkeys(h.payload["belge_id"] for h in aday))[:k_karar]
        # 2) Cevabı HÜKÜMDEN ver: bağlama şikâyet/savunma (taraf beyanı) değil, o kararın hüküm
        #    bölümü + en iyi eşleşen Kurul değerlendirmesi girer. Aksi halde model veri sorumlusunun
        #    savunmasını Kurul görüşü gibi aktarıyordu (KARARLAR.md 2026-11-12).
        karar: list[Hit] = []
        for bid in sira:
            en_iyi = next(h for h in aday if h.payload["belge_id"] == bid)
            deg = [h for h in aday if h.payload["belge_id"] == bid and h.payload["bolum"] == "degerlendirme"][:per_karar - 1]
            pts, _ = self.client.scroll(self.name, scroll_filter=models.Filter(must=[
                models.FieldCondition(key="belge_id", match=models.MatchValue(value=bid)),
                models.FieldCondition(key="bolum", match=models.MatchValue(value="hukum")),
            ]), limit=4, with_payload=True)
            hukum = sorted((Hit(en_iyi.score, p.payload) for p in pts), key=lambda h: h.payload["chunk_id"])[:2]
            karar += deg + hukum if hukum else [en_iyi]
        ctx = {"mevzuat": mevzuat, "karar": karar}
        return trim_context(ctx, max_chars) if max_chars else ctx


def trim_context(ctx: dict[str, list[Hit]], max_chars: int = 14000) -> dict[str, list[Hit]]:
    """Bağlam bütçesi (yerel modelin 8k penceresi için): aşılırsa en düşük sıralı kaynaklar atılır.

    Yalnız bağlama GERÇEKTEN girecek kanallarla çağrılmalı: eşikle elenen karar kanalı bütçeden pay
    alınca mevzuat 2 kaynağa düşüyor, cevabı taşıyan madde dışarıda kalıyordu (ölçüldü, 13 Kas).
    """
    mevzuat, karar = list(ctx.get("mevzuat", [])), list(ctx.get("karar", []))

    def size(hs: list[Hit]) -> int:
        return sum(len(h.payload["metin"]) for h in hs)
    while size(mevzuat) + size(karar) > max_chars and (len(mevzuat) > 2 or len(karar) > 2):
        if len(karar) > 2 and (len(mevzuat) <= 2 or size(karar) >= size(mevzuat)):
            karar.pop()
        else:
            mevzuat.pop()
    return {"mevzuat": mevzuat, "karar": karar}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--mode", default="hibrit")
    ap.add_argument("--method", choices=["dense", "bm25", "hybrid"], default="hybrid")
    ap.add_argument("-k", type=int, default=5)
    args = ap.parse_args()
    for i, h in enumerate(Searcher(args.mode).search(args.query, args.method, args.k), 1):
        print(f"{i}. {h.score:.4f}  {h.payload['atif']}  — {h.payload['metin'][:120]}")


if __name__ == "__main__":
    main()
