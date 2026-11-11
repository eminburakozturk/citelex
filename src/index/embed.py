"""bge-m3 embedding + kalıcı önbellek.

Önbellek anahtarı sha256(model | max_length | metin). Hem dense (1024, normalize) hem sparse
(lexical weights) saklanır; sparse şimdilik indekse girmez, 17 Kas "BM25 vs bge-m3 sparse"
karşılaştırması için tutulur. Artımlı güncellemede yalnızca yeni/değişen metinler modele gider.

Önbellek: data/index/emb_cache.sqlite (git'e girmez).
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import numpy as np

MODEL_NAME = "BAAI/bge-m3"
MAX_LENGTH = 2048
DIM = 1024
CACHE_PATH = Path("data/index/emb_cache.sqlite")


def _key(text: str) -> str:
    return hashlib.sha256(f"{MODEL_NAME}|{MAX_LENGTH}|{text}".encode("utf-8")).hexdigest()


class Embedder:
    def __init__(self, cache_path: Path = CACHE_PATH, batch_size: int = 16):
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(cache_path)
        self.db.execute("CREATE TABLE IF NOT EXISTS emb (key TEXT PRIMARY KEY, dense BLOB, sparse TEXT)")
        self.batch_size = batch_size
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from FlagEmbedding import BGEM3FlagModel
            self._model = BGEM3FlagModel(MODEL_NAME, use_fp16=True)
        return self._model

    def _encode(self, texts: list[str]) -> tuple[np.ndarray, list[dict[str, float]]]:
        out = self.model.encode(
            texts, batch_size=self.batch_size, max_length=MAX_LENGTH,
            return_dense=True, return_sparse=True, return_colbert_vecs=False,
        )
        dense = np.asarray(out["dense_vecs"], dtype=np.float32)
        sparse = [{str(k): float(v) for k, v in d.items()} for d in out["lexical_weights"]]
        return dense, sparse

    def embed(self, texts: list[str]) -> tuple[np.ndarray, list[dict[str, float]], int]:
        """(dense [n, DIM], sparse listesi, modele giden metin sayısı)."""
        keys = [_key(t) for t in texts]
        found: dict[str, tuple[np.ndarray, dict]] = {}
        for i in range(0, len(keys), 500):
            part = keys[i:i + 500]
            q = f"SELECT key, dense, sparse FROM emb WHERE key IN ({','.join('?' * len(part))})"
            for k, d, s in self.db.execute(q, part):
                found[k] = (np.frombuffer(d, dtype=np.float32), json.loads(s))
        todo = list(dict.fromkeys(k for k in keys if k not in found))
        if todo:
            text_of = dict(zip(keys, texts))
            dense, sparse = self._encode([text_of[k] for k in todo])
            rows = [(k, dense[i].tobytes(), json.dumps(sparse[i])) for i, k in enumerate(todo)]
            self.db.executemany("INSERT OR REPLACE INTO emb VALUES (?, ?, ?)", rows)
            self.db.commit()
            for i, k in enumerate(todo):
                found[k] = (dense[i], sparse[i])
        return np.stack([found[k][0] for k in keys]), [found[k][1] for k in keys], len(todo)

    def embed_query(self, text: str) -> np.ndarray:
        """Sorgular önbelleğe alınmaz."""
        return self._encode([text])[0][0]
