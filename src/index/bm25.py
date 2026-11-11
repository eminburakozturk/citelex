"""BM25'i Qdrant sparse vektörüne çevirme.

Ayrım (KARARLAR.md):
  - TF kısmı istemcide: w(t, d) = tf * (k1 + 1) / (tf + k1 * (1 - b + b * |d| / avgdl))
  - IDF kısmı Qdrant'ta: sparse vektör `modifier=IDF` ile sunucu hesaplar.
  - avgdl koleksiyon kurulurken sabitlenir (BM25Params dosyası), artımlı upsert'te değişmez;
    tam yeniden kurulumda yeniden hesaplanır.
Sorgu vektörü: her benzersiz terim için ağırlık 1 (IDF sunucuda çarpılır).

Terim kimliği: blake2b ile 32 bit tamsayı (sözlük tutmaya gerek yok; çakışma olasılığı bu ölçekte ihmal edilebilir).
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from .tokenize import TOKENIZER_VERSION, tokenize


@dataclass
class BM25Params:
    k1: float
    b: float
    avgdl: float
    n_docs: int
    tokenizer: str = TOKENIZER_VERSION

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "BM25Params":
        p = cls(**json.loads(path.read_text(encoding="utf-8")))
        if p.tokenizer != TOKENIZER_VERSION:
            raise RuntimeError(f"tokenizer {p.tokenizer} != {TOKENIZER_VERSION}: tam yeniden kurulum gerekli")
        return p


def term_id(term: str) -> int:
    return int.from_bytes(hashlib.blake2b(term.encode("utf-8"), digest_size=4).digest(), "little")


def fit(texts: list[str], k1: float = 1.2, b: float = 0.75) -> BM25Params:
    lens = [len(tokenize(t)) for t in texts]
    return BM25Params(k1=k1, b=b, avgdl=sum(lens) / len(lens), n_docs=len(lens))


def _sparse(weights: dict[int, float]) -> tuple[list[int], list[float]]:
    idx = sorted(weights)
    return idx, [weights[i] for i in idx]


def doc_vector(text: str, p: BM25Params) -> tuple[list[int], list[float]]:
    toks = tokenize(text)
    dl = len(toks)
    norm = p.k1 * (1 - p.b + p.b * dl / p.avgdl)
    w: dict[int, float] = {}
    for term, tf in Counter(toks).items():
        tid = term_id(term)
        w[tid] = w.get(tid, 0.0) + tf * (p.k1 + 1) / (tf + norm)
    return _sparse(w)


def query_vector(text: str) -> tuple[list[int], list[float]]:
    return _sparse({term_id(t): 1.0 for t in set(tokenize(text))})
