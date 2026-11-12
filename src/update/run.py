"""Kendini güncelleme: kaynakları kontrol et -> değişeni yeniden işle -> indeksi artımlı güncelle -> regresyon.

Akış (PLAN.md):
  1. Her doküman indirilir (src/sources/http.py: tanımlayıcı UA, host başına 2 sn, robots.txt).
  2. İçerik hash'i hesaplanır (mevzuat: PDF metni; karar: çıkarılmış metin). Aktif sürümle aynıysa dur.
     GeneratePdf her indirmede farklı bayt verir; bu durum 'bayt_farkli_icerik_ayni' olarak kaydedilir.
  3. Değiştiyse: ham dosya data/raw/versions/ altına saklanır, data/raw/... güncel dosya değiştirilir,
     eski sürüm 'eski' işaretlenir (silinmez).
  4. En az bir değişiklik varsa ayrıştırma + parçalama yeniden çalışır (tüm derlem; saniyeler sürer), ardından
     indeks Qdrant'taki chunk_id -> content_hash durumuyla karşılaştırılır: yalnız yeni/değişen parçalar
     embed edilip yazılır, artık olmayan parçalar silinir. BM25 avgdl DEĞİŞMEZ (KARARLAR.md).
  5. Arama regresyonu (eval/retrieval_check) çalışır; isabet önceki çalıştırmadan düşükse uyarı verilir.
  6. Özet logs/updates.jsonl'e ve SQLite runs tablosuna yazılır.

Kullanım:
  python -m src.update.run --init                     # mevcut yerel dosyaları ilk sürüm olarak kaydet (indirme yok)
  python -m src.update.run                            # günlük kontrol
  python -m src.update.run --sadece karar:2023-2007   # tek doküman
  python -m src.update.run --sahte karar:2023-2007=yol/dosya.txt   # test: indirme yerine yerel içerik kullan
  python -m src.update.run --llm-eval                 # regresyona uçtan uca eval'i de ekle (yavaş)
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

import httpx
import pdfplumber

from src.sources import kvkk
from src.sources.http import FetchError, get
from src.store import db

PY = sys.executable
LOG = Path("logs/updates.jsonl")
VERS = Path("data/raw/versions")
MODE = "hibrit"


# ---------- izlenen dokümanlar ----------

def tracked() -> list[dict]:
    out = []
    src = json.load(open("configs/sources.json", encoding="utf-8"))
    for fname, v in src.items():
        if fname.startswith("_") or "url" not in v:
            continue
        out.append({"doc_key": f"mevzuat:{fname}", "kind": "mevzuat", "belge_id": v["belge_id"], "url": v["url"],
                    "local_path": f"data/raw/{fname}"})
    for k in json.load(open("configs/kvkk_kararlar.json", encoding="utf-8"))["kararlar"]:
        stem = k["dosya"].replace(".html", "")
        out.append({"doc_key": f"karar:{stem.replace('karar_', '')}", "kind": "karar",
                    "belge_id": "kvkk-karar-" + k["karar_no"].replace("/", "-"), "url": k["url"],
                    "local_path": f"data/raw/kvkk_karar/{stem}.txt"})
    return out


# ---------- içerik ----------

def pdf_text(data: bytes) -> str:
    with pdfplumber.open(io.BytesIO(data)) as p:
        return "\n".join(pg.extract_text() or "" for pg in p.pages)


def content_of(doc: dict, raw: bytes) -> str:
    text = pdf_text(raw) if doc["kind"] == "mevzuat" else raw.decode("utf-8")
    return re.sub(r"\s+", " ", text).strip()


def sha(b: bytes | str) -> str:
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()


def fetch_raw(doc: dict, client: httpx.Client) -> bytes:
    if doc["kind"] == "mevzuat":
        r = get(doc["url"], client=client)
        if not r.headers.get("content-type", "").startswith("application/pdf"):
            raise FetchError(f"PDF değil ({r.headers.get('content-type')})")
        return r.content
    txt = kvkk.fetch_decision(doc["url"], client)
    if not txt:
        raise FetchError("karar içerik kabı bulunamadı (sayfa yapısı değişmiş olabilir)")
    return txt.encode("utf-8")


def archive(doc: dict, raw: bytes, chash: str) -> str:
    ext = Path(doc["local_path"]).suffix
    d = VERS / doc["doc_key"].replace(":", "_")
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{datetime.now():%Y%m%d}_{chash[:10]}{ext}"
    p.write_bytes(raw)
    return str(p)


# ---------- adımlar ----------

def init(con) -> None:
    n = 0
    for doc in tracked():
        con.execute("INSERT OR IGNORE INTO documents VALUES (?,?,?,?,?,?)",
                    (doc["doc_key"], doc["kind"], doc["belge_id"], doc["url"], doc["local_path"], db.now()))
        if db.active_version(con, doc["doc_key"]):
            continue
        raw = Path(doc["local_path"]).read_bytes()
        chash = sha(content_of(doc, raw))
        db.set_active(con, doc["doc_key"], chash, sha(raw), archive(doc, raw, chash))
        n += 1
    con.commit()
    print(f"{n} doküman ilk sürüm olarak kaydedildi; toplam {con.execute('SELECT COUNT(*) FROM documents').fetchone()[0]}")


def check(con, run_id: str, docs: list[dict], fake: dict[str, str]) -> tuple[list[dict], int]:
    changed, errors = [], 0
    with httpx.Client() as client:
        for doc in docs:
            try:
                raw = Path(fake[doc["doc_key"]]).read_bytes() if doc["doc_key"] in fake else fetch_raw(doc, client)
                chash = sha(content_of(doc, raw))
                act = db.active_version(con, doc["doc_key"])
                if act and act["content_hash"] == chash:
                    result = "ayni" if act["raw_sha"] == sha(raw) else "bayt_farkli_icerik_ayni"
                    detail = None
                else:
                    raw_path = archive(doc, raw, chash)
                    Path(doc["local_path"]).write_bytes(raw)
                    result = db.set_active(con, doc["doc_key"], chash, sha(raw), raw_path)
                    detail = f"{(act['content_hash'][:10] if act else '-')} -> {chash[:10]}"
                    changed.append(doc)
            except Exception as e:  # noqa: BLE001 — bir kaynağın hatası diğerlerini durdurmaz (PLAN.md)
                result, detail = "hata", f"{type(e).__name__}: {str(e)[:200]}"
                errors += 1
            con.execute("INSERT INTO checks VALUES (?,?,?,?,?)", (run_id, doc["doc_key"], db.now(), result, detail))
            con.commit()
            print(f"  {doc['doc_key']:42} {result}" + (f"  ({detail})" if detail else ""), flush=True)
    return changed, errors


def rebuild_chunks(changed: list[dict]) -> None:
    kinds = {d["kind"] for d in changed}
    steps = []
    if "mevzuat" in kinds:
        steps += [["-m", "src.ingest.parse"]] + [["-m", "src.ingest.chunk", "--mode", m] for m in ("madde", "fikra", "hibrit")]
    if "karar" in kinds:
        steps += [["-m", "src.ingest.parse_karar"]]
    for s in steps:
        r = subprocess.run([PY, *s], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            raise RuntimeError(f"{' '.join(s)} başarısız:\n{r.stderr[-1500:]}")


def reindex() -> dict:
    """Qdrant durumuyla dosyadaki güncel parçaları karşılaştır; yalnız farkı yaz/sil."""
    from qdrant_client import QdrantClient, models

    from src.index import bm25
    from src.index.build import (QDRANT_URL, collection_name, content_hash, indexed_state, load_chunks,
                                 params_path, point_id, upsert_chunks)
    name = collection_name(MODE)
    client = QdrantClient(url=QDRANT_URL)
    params = bm25.BM25Params.load(params_path(MODE))  # avgdl sabit
    chunks, _ = load_chunks(MODE)
    state = indexed_state(client, name)
    want = {c["chunk_id"]: c for c in chunks}
    yeni = [c for cid, c in want.items() if cid not in state]
    degisen = [c for cid, c in want.items() if cid in state and state[cid] != content_hash(c)]
    silinen = [cid for cid in state if cid not in want]
    n_embed, t_emb = upsert_chunks(client, name, yeni + degisen, params)
    if silinen:
        client.delete(name, points_selector=models.PointIdsList(points=[point_id(c) for c in silinen]), wait=True)
    return {"koleksiyon": name, "toplam": len(want), "yeni": len(yeni), "degisen": len(degisen), "silinen": len(silinen),
            "embed_edilen": n_embed, "embed_sn": round(t_emb, 1),
            "ornek": [c["chunk_id"] for c in (yeni + degisen)[:5]] + [f"-{c}" for c in silinen[:5]]}


def regression(con, run_eval_llm: bool) -> dict:
    out_md = "results/update_retrieval_check.md"
    r = subprocess.run([PY, "-m", "eval.retrieval_check", "--out", out_md], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    res = {}
    for kanal, line in re.findall(r"^(mevzuat|karar) isabet \(\d+ soru\): (.+)$", r.stdout, re.M):
        res[kanal] = {m: int(h) for m, h in re.findall(r"(\w+) (\d+)/\d+", line)}
    if run_eval_llm:
        e = subprocess.run([PY, "-m", "eval.run_eval"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        hist = Path("results/eval_history.jsonl").read_text(encoding="utf-8").splitlines() if e.returncode == 0 else []
        res["uctan_uca"] = json.loads(hist[-1]) if hist else {"hata": e.stderr[-300:]}
    prev = con.execute("SELECT eval FROM runs WHERE eval IS NOT NULL AND finished IS NOT NULL ORDER BY started DESC LIMIT 1").fetchone()
    uyari = []
    if prev:
        p = json.loads(prev["eval"])
        for kanal in ("mevzuat", "karar"):
            for m, v in res.get(kanal, {}).items():
                if v < p.get(kanal, {}).get(m, v):
                    uyari.append(f"{kanal}/{m}: {p[kanal][m]} -> {v}")
    res["uyari"] = uyari
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--sadece", nargs="*", default=None, help="yalnız bu doc_key'ler")
    ap.add_argument("--sahte", nargs="*", default=[], help="doc_key=yerel_dosya (test)")
    ap.add_argument("--llm-eval", action="store_true")
    ap.add_argument("--eval-her-zaman", action="store_true", help="değişiklik olmasa da regresyon çalıştır")
    args = ap.parse_args()

    con = db.connect()
    if args.init:
        init(con)
        return
    fake = dict(s.split("=", 1) for s in args.sahte)
    docs = [d for d in tracked() if args.sadece is None or d["doc_key"] in args.sadece or d["doc_key"] in fake]
    unknown = [d["doc_key"] for d in docs if not db.active_version(con, d["doc_key"])]
    if unknown:
        raise SystemExit(f"Depoda kaydı olmayan doküman var ({len(unknown)}); önce --init çalıştırın.")

    run_id = f"{datetime.now():%Y%m%dT%H%M%S}-{uuid.uuid4().hex[:4]}"
    con.execute("INSERT INTO runs (run_id, started, note) VALUES (?,?,?)",
                (run_id, db.now(), "sahte: " + ",".join(fake) if fake else None))
    con.commit()
    t0 = time.time()
    print(f"[{run_id}] {len(docs)} doküman kontrol ediliyor")
    changed, errors = check(con, run_id, docs, fake)

    diff, ev = None, None
    if changed:
        rebuild_chunks(changed)
        diff = reindex()
        print("  indeks:", diff)
    if changed or args.eval_her_zaman:
        ev = regression(con, args.llm_eval)
        print("  regresyon:", {k: v for k, v in ev.items() if k != "uctan_uca"})
        if ev["uyari"]:
            print("  UYARI: arama isabeti düştü ->", ev["uyari"])

    con.execute("UPDATE runs SET finished=?, n_checked=?, n_changed=?, n_error=?, index_diff=?, eval=? WHERE run_id=?",
                (db.now(), len(docs), len(changed), errors, json.dumps(diff, ensure_ascii=False) if diff else None,
                 json.dumps(ev, ensure_ascii=False) if ev else None, run_id))
    con.commit()
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"run_id": run_id, "tarih": db.now(), "sure_sn": round(time.time() - t0, 1),
                             "kontrol": len(docs), "degisen": [d["doc_key"] for d in changed], "hata": errors,
                             "sahte": list(fake) or None, "indeks": diff, "regresyon": ev}, ensure_ascii=False) + "\n")
    print(f"[{run_id}] bitti: {len(changed)} değişti, {errors} hata, {time.time() - t0:.0f} sn")
    if errors and errors == len(docs):
        sys.exit(2)  # tüm kaynaklar hatalı: zamanlayıcı başarısız saysın


if __name__ == "__main__":
    main()
