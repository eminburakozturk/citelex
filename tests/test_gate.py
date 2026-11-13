"""Arama kapısının kendisinin testi: temel değerde yeşil, bozulmuş tokenizer'da kırmızı (Qdrant/model gerekmez)."""
from __future__ import annotations

import sys

from eval import gate
from src.index import bm25


def test_kapi_temelde_yesil(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["gate"])
    assert gate.main() == 0


def test_kapi_bozuk_tokenizerda_kirmizi(monkeypatch):
    # Türkçe küçük harfe çevirme ve ek/noktalama ayıklama olmadan basit boşluk bölme: isabet düşmeli.
    monkeypatch.setattr(bm25, "tokenize", lambda t: t.split())
    monkeypatch.setattr(sys, "argv", ["gate"])
    assert gate.main() == 1
