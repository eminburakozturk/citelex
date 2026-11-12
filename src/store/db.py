"""Doküman deposu ve sürümleme (SQLite, data/store/citelex.db — git dışı).

documents : izlenen her kaynak (mevzuat PDF'i veya KVKK karar sayfası)
versions  : her doküman için içerik sürümleri. content_hash = AYRIŞTIRILMIŞ METNİN hash'i
            (ham dosya hash'i değil: GeneratePdf her indirmede farklı bayt üretir). Ham dosya
            data/raw/versions/<doc>/ altında saklanır. Eski sürüm SİLİNMEZ, status='eski' olur.
runs      : her güncelleme çalıştırmasının özeti (kontrol/değişiklik/hata sayıları, indeks farkı, eval)
checks    : çalıştırma içinde doküman başına sonuç
"""
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/store/citelex.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    doc_key     TEXT PRIMARY KEY,           -- 'mevzuat:1.5.6698.pdf' | 'karar:2023-2007'
    kind        TEXT NOT NULL,              -- 'mevzuat' | 'karar'
    belge_id    TEXT NOT NULL,
    url         TEXT NOT NULL,
    local_path  TEXT NOT NULL,              -- ayrıştırma hattının okuduğu güncel dosya
    added_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS versions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_key      TEXT NOT NULL REFERENCES documents(doc_key),
    content_hash TEXT NOT NULL,
    raw_sha      TEXT NOT NULL,
    raw_path     TEXT NOT NULL,
    first_seen   TEXT NOT NULL,
    status       TEXT NOT NULL CHECK (status IN ('aktif', 'eski')),
    UNIQUE (doc_key, content_hash)
);
CREATE TABLE IF NOT EXISTS runs (
    run_id      TEXT PRIMARY KEY,
    started     TEXT NOT NULL,
    finished    TEXT,
    n_checked   INTEGER, n_changed INTEGER, n_error INTEGER,
    index_diff  TEXT,                       -- JSON: eklenen/güncellenen/silinen parça sayıları
    eval        TEXT,                       -- JSON: regresyon sonucu
    note        TEXT
);
CREATE TABLE IF NOT EXISTS checks (
    run_id     TEXT NOT NULL REFERENCES runs(run_id),
    doc_key    TEXT NOT NULL,
    checked_at TEXT NOT NULL,
    result     TEXT NOT NULL,               -- 'ayni' | 'bayt_farkli_icerik_ayni' | 'yeni_surum' | 'eski_surume_dondu' | 'hata'
    detail     TEXT
);
"""


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def active_version(con: sqlite3.Connection, doc_key: str) -> sqlite3.Row | None:
    return con.execute("SELECT * FROM versions WHERE doc_key=? AND status='aktif'", (doc_key,)).fetchone()


def set_active(con: sqlite3.Connection, doc_key: str, content_hash: str, raw_sha: str, raw_path: str) -> str:
    """Bu içeriği aktif sürüm yap. Dönen: 'yeni_surum' | 'eski_surume_dondu'."""
    con.execute("UPDATE versions SET status='eski' WHERE doc_key=? AND status='aktif'", (doc_key,))
    row = con.execute("SELECT id FROM versions WHERE doc_key=? AND content_hash=?", (doc_key, content_hash)).fetchone()
    if row:  # daha önce görülmüş içerik (ör. geri alınan değişiklik): yeniden aktifleştir
        con.execute("UPDATE versions SET status='aktif' WHERE id=?", (row["id"],))
        return "eski_surume_dondu"
    con.execute("INSERT INTO versions (doc_key, content_hash, raw_sha, raw_path, first_seen, status) VALUES (?,?,?,?,?, 'aktif')",
                (doc_key, content_hash, raw_sha, raw_path, now()))
    return "yeni_surum"
