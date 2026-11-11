"""Arama: dense, bm25 veya hibrit (RRF, k=60).

Varsayılan filtre (iki alt aramaya da uygulanır): mulga=false VE diger_kanuna_islendi=false.
Opsiyonel: belge_tur (kanun/yonetmelik/teblig) filtresi.

Kullanım: python -m src.retrieve.search "yıllık izin kaç gün" --mode hibrit --method hybrid
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass

from qdrant_client import QdrantClient, models

from src.index import bm25
from src.index.build import QDRANT_URL, collection_name
from src.index.embed import Embedder

RRF_K = 60
PREFETCH = 50


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

    def search(self, query: str, method: str = "hybrid", top_k: int = 10,
               belge_tur: list[str] | None = None, include_inactive: bool = False) -> list[Hit]:
        flt = build_filter(belge_tur, include_inactive)
        idx, val = bm25.query_vector(query)
        sparse = models.SparseVector(indices=idx, values=val)
        if method == "bm25":
            res = self.client.query_points(self.name, query=sparse, using="bm25",
                                           query_filter=flt, limit=top_k, with_payload=True)
        else:
            dense = self.embedder.embed_query(query).tolist()
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
