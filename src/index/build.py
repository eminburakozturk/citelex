"""chunks_<mode>.jsonl -> Qdrant koleksiyonu `citelex_<mode>` (dense + BM25 sparse).

  --recreate : tam yeniden kurulum; koleksiyon silinip kurulur, BM25 avgdl yeniden hesaplanır.
  (varsayılan): upsert; avgdl data/index/bm25_<mode>.json'dan okunur, DEĞİŞMEZ.

Nokta kimliği chunk_id'den UUID5: aynı parça tekrar yazılınca üzerine yazılır.

Kullanım: python -m src.index.build --mode hibrit --recreate
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import uuid
from pathlib import Path

from qdrant_client import QdrantClient, models

from . import bm25
from .embed import DIM, Embedder

from src.config import QDRANT_URL  # noqa: E402  (.env okunur; localhost -> 127.0.0.1)
NS = uuid.UUID("6f0c2b52-58c6-4a8e-9a43-1f0e3c7d9b21")  # citelex chunk namespace (sabit)

PAYLOAD_KEYS = [
    "chunk_id", "belge_id", "belge_tur", "belge_no", "belge_adi", "madde_tur", "madde_no",
    "fikra_no", "parca_no", "giris", "baslik", "bolum", "atif", "mulga", "diger_kanuna_islendi", "dipnotlar", "metin",
    "kategori", "url", "karar_tarihi",  # yalnız karar parçalarında dolu
]
KARAR_CHUNKS = Path("data/processed/chunks_karar.jsonl")  # mod bağımsız; her koleksiyona eklenir
INDEXES = {
    "belge_tur": models.PayloadSchemaType.KEYWORD,
    "belge_id": models.PayloadSchemaType.KEYWORD,
    "katman": models.PayloadSchemaType.KEYWORD,
    # Qdrant Cloud filtrelenen her alan için indeks ister (yerel sürüm istemez): madde genişletme ve /kaynak filtreleri
    "madde_tur": models.PayloadSchemaType.KEYWORD,
    "madde_no": models.PayloadSchemaType.KEYWORD,
    "bolum": models.PayloadSchemaType.KEYWORD,
    "mulga": models.PayloadSchemaType.BOOL,
    "diger_kanuna_islendi": models.PayloadSchemaType.BOOL,
}


def collection_name(mode: str) -> str:
    return f"citelex_{mode}"


def params_path(mode: str) -> Path:
    return Path(f"data/index/bm25_{mode}.json")


def point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(NS, chunk_id))


def create_collection(client: QdrantClient, name: str) -> None:
    if client.collection_exists(name):
        client.delete_collection(name)
    client.create_collection(
        name,
        vectors_config={"dense": models.VectorParams(size=DIM, distance=models.Distance.COSINE)},
        sparse_vectors_config={"bm25": models.SparseVectorParams(modifier=models.Modifier.IDF)},
    )
    for field, schema in INDEXES.items():
        client.create_payload_index(name, field, field_schema=schema)


def load_chunks(mode: str, with_karar: bool = True) -> tuple[list[dict], int]:
    """Bir koleksiyonun güncel parça listesi (mevzuat + karar) ve mevzuat parça sayısı."""
    chunks = [json.loads(l) for l in open(f"data/processed/chunks_{mode}.jsonl", encoding="utf-8")]
    n_mevzuat = len(chunks)
    if with_karar and KARAR_CHUNKS.exists():
        chunks += [json.loads(l) for l in open(KARAR_CHUNKS, encoding="utf-8")]
    return chunks, n_mevzuat


def content_hash(chunk: dict) -> str:
    return hashlib.sha256(chunk["embed_text"].encode("utf-8")).hexdigest()


def upsert_chunks(client: QdrantClient, name: str, chunks: list[dict], params: bm25.BM25Params,
                  embedder: Embedder | None = None) -> tuple[int, float]:
    """Parçaları yaz (aynı chunk_id -> üzerine yazar). (modele giden yeni metin sayısı, embed süresi)."""
    if not chunks:
        return 0, 0.0
    texts = [c["embed_text"] for c in chunks]
    t0 = time.time()
    dense, _sparse, n_new = (embedder or Embedder()).embed(texts)
    t_emb = time.time() - t0
    points = []
    for c, vec, text in zip(chunks, dense, texts):
        idx, val = bm25.doc_vector(text, params)
        payload = {k: c.get(k) for k in PAYLOAD_KEYS}
        payload["katman"] = "derin"
        payload["content_hash"] = content_hash(c)
        points.append(models.PointStruct(
            id=point_id(c["chunk_id"]),
            vector={"dense": vec.tolist(), "bm25": models.SparseVector(indices=idx, values=val)},
            payload=payload,
        ))
    for i in range(0, len(points), 128):
        client.upsert(name, points[i:i + 128], wait=True)
    return n_new, t_emb


def indexed_state(client: QdrantClient, name: str) -> dict[str, str]:
    """Koleksiyondaki chunk_id -> content_hash (artımlı güncellemenin karşılaştırma tabanı)."""
    state, offset = {}, None
    while True:
        pts, offset = client.scroll(name, limit=1000, offset=offset, with_payload=["chunk_id", "content_hash"],
                                    with_vectors=False)
        state.update({p.payload["chunk_id"]: p.payload["content_hash"] for p in pts})
        if offset is None:
            return state


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["madde", "fikra", "hibrit"], default="hibrit")
    ap.add_argument("--recreate", action="store_true")
    ap.add_argument("--no-karar", action="store_true", help="KVKK karar parçalarını ekleme")
    args = ap.parse_args()

    chunks, n_mevzuat = load_chunks(args.mode, not args.no_karar)
    texts = [c["embed_text"] for c in chunks]
    name = collection_name(args.mode)
    client = QdrantClient(url=QDRANT_URL)

    if args.recreate:
        params = bm25.fit(texts)
        params.save(params_path(args.mode))
        create_collection(client, name)
    else:
        params = bm25.BM25Params.load(params_path(args.mode))

    n_new, t_emb = upsert_chunks(client, name, chunks, params)

    info = client.get_collection(name)
    print(f"{name}: {info.points_count} nokta ({n_mevzuat} mevzuat + {len(chunks) - n_mevzuat} karar) | "
          f"embed: {n_new} yeni / {len(texts)} ({t_emb:.1f} sn) | "
          f"BM25 k1={params.k1} b={params.b} avgdl={params.avgdl:.1f} (N={params.n_docs})")


if __name__ == "__main__":
    main()
