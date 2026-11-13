"""Ortam ayarları. .env dosyası (git dışı) okunur; var olan ortam değişkenleri ezilmez.

Anahtarlar yalnızca .env'de durur; hiçbir yerde yazdırılmaz/loglanmaz.
"""
from __future__ import annotations

import os
from pathlib import Path


def load_env(path: str = ".env") -> None:
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_env()

# 127.0.0.1: Windows'ta "localhost" önce IPv6'ya (::1) gidip istek başına saniyeler kaybettirebiliyor.
QDRANT_URL = os.environ.get("QDRANT_URL", "http://127.0.0.1:6333").replace("//localhost", "//127.0.0.1")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY") or None   # yalnız Qdrant Cloud (yayın); yerelde boş
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").replace("//localhost", "//127.0.0.1")
if not OLLAMA_HOST.startswith("http"):
    OLLAMA_HOST = "http://" + OLLAMA_HOST
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
