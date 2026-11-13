"""Yerel Qdrant koleksiyonunu Qdrant Cloud'a kopyalar (vektörler dahil; yeniden embedding yok).

Yerel indeks tek doğruluk kaynağıdır: günlük güncelleme yereli değiştirir, bu betik farkı buluta taşır
(chunk_id -> content_hash karşılaştırması; yalnız yeni/değişen noktalar yazılır, artık olmayanlar silinir).

Kullanım: python -m scripts.yayin_qdrant [--recreate]
Gerekli ortam (.env): QDRANT_CLOUD_URL, QDRANT_CLOUD_API_KEY
"""
from __future__ import annotations

import argparse
import os
import re

from qdrant_client import QdrantClient, models

from src import config
from src.index.build import INDEXES, collection_name, create_collection, indexed_state, point_id


def cloud_client() -> QdrantClient:
    url = re.sub(r"^(https?:/*)+", "https://", os.environ.get("QDRANT_CLOUD_URL", "").strip())
    key = os.environ.get("QDRANT_CLOUD_API_KEY", "").strip()
    if not url or not key:
        raise SystemExit("QDRANT_CLOUD_URL / QDRANT_CLOUD_API_KEY yok (.env)")
    return QdrantClient(url=url, api_key=key, timeout=120)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="hibrit")
    ap.add_argument("--recreate", action="store_true")
    args = ap.parse_args()
    name = collection_name(args.mode)
    local, cloud = QdrantClient(url=config.QDRANT_URL), cloud_client()
    if args.recreate or not cloud.collection_exists(name):
        create_collection(cloud, name)
    for field, schema in INDEXES.items():   # var olan indeks yeniden oluşturulmaz (idempotent)
        cloud.create_payload_index(name, field, field_schema=schema, wait=True)
        local.create_payload_index(name, field, field_schema=schema, wait=True)
    want, have = indexed_state(local, name), indexed_state(cloud, name)
    yaz = {point_id(c) for c, h in want.items() if have.get(c) != h}
    sil = [point_id(c) for c in have if c not in want]
    n, offset = 0, None
    while True:
        pts, offset = local.scroll(name, limit=128, offset=offset, with_payload=True, with_vectors=True)
        batch = [models.PointStruct(id=p.id, vector=p.vector, payload=p.payload) for p in pts if p.id in yaz]
        if batch:
            cloud.upsert(name, batch, wait=True)
            n += len(batch)
        if offset is None:
            break
    if sil:
        cloud.delete(name, points_selector=models.PointIdsList(points=sil), wait=True)
    info = cloud.get_collection(name)
    print(f"{name}: yazılan {n}, silinen {len(sil)}, bulutta {info.points_count} nokta (yerelde {len(want)}), durum {info.status}")


if __name__ == "__main__":
    main()
