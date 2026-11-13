""""Bu madde değişti": iki sürüm arasında madde (mevzuat) / bölüm (karar) düzeyinde kelime farkı.

Güncelleme hattı yeni bir sürümü aktif yaptığında (src/update/run.py) eski ve yeni ham dosyalar ayrıştırılır,
birimler eşleştirilir ve fark data/store/farklar/<fark_id>.json olarak yazılır. API (GET /degisiklikler,
GET /degisiklik/{fark_id}) yalnız bu JSON'ları okur: yayın ortamında ham sürüm dosyaları olmasa da çalışır.

Birim anahtarı: mevzuat "madde_tur:madde_no" (ör. "asil:5", "gecici:1"); karar bölüm adı (sikayet, savunma,
degerlendirme, hukum). Fark kelime düzeyinde: [["=", "..."], ["-", "silinen"], ["+", "eklenen"], ...].

Kullanım:
  python -m src.update.diff --doc karar:2023-2007        # bu dokümanın sürüm geçişlerinin farkını (yeniden) üret
  python -m src.update.diff --hepsi                       # checks tablosundaki tüm sürüm geçişleri
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
from datetime import datetime
from pathlib import Path

from src.store import db

FARK_DIR = Path("data/store/farklar")


def units(kind: str, path: Path, belge_id: str) -> dict[str, dict]:
    """Ham dosya -> {birim_anahtari: {"etiket", "metin"}}."""
    if kind == "mevzuat":
        from src.ingest.parse import load_sources, parse
        meta = next(v for v in load_sources().values() if v.get("belge_id") == belge_id)
        out = {}
        for a in parse(path, meta):
            key = f"{a.madde_tur}:{a.madde_no}"
            metin = "\n".join(f["metin"] for f in a.fikralar)
            etiket = f"{a.kisa_ad} m. {a.madde_no}" + (f" ({a.baslik})" if a.baslik else "")
            if key in out:  # aynı numara iki kez (nadir): metni birleştir
                out[key]["metin"] += "\n" + metin
            else:
                out[key] = {"etiket": etiket, "metin": metin}
        return out
    from src.ingest.parse_karar import read_decision, split_sections
    d = read_decision(path)
    out = {}
    for sec, lines in split_sections(d["body"]):
        metin = "\n".join(lines).strip()
        out[sec] = {"etiket": sec, "metin": (out[sec]["metin"] + "\n" + metin) if sec in out else metin}
    return out


def word_diff(a: str, b: str) -> list[list[str]]:
    ta, tb = re.findall(r"\S+|\s+", a), re.findall(r"\S+|\s+", b)
    ops: list[list[str]] = []

    def add(op: str, toks: list[str]) -> None:
        s = "".join(toks)
        if not s:
            return
        if ops and ops[-1][0] == op:
            ops[-1][1] += s
        else:
            ops.append([op, s])

    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        if tag == "equal":
            add("=", ta[i1:i2])
        else:
            add("-", ta[i1:i2])
            add("+", tb[j1:j2])
    return ops


def compare(kind: str, belge_id: str, eski: Path, yeni: Path) -> list[dict]:
    ua, ub = units(kind, eski, belge_id), units(kind, yeni, belge_id)
    out = []
    for key in list(dict.fromkeys([*ua, *ub])):
        a, b = ua.get(key), ub.get(key)
        if a and b and re.sub(r"\s+", " ", a["metin"]).strip() == re.sub(r"\s+", " ", b["metin"]).strip():
            continue
        durum = "eklendi" if a is None else "silindi" if b is None else "degisti"
        out.append({"birim": key, "etiket": (b or a)["etiket"], "durum": durum,
                    "eski": a["metin"] if a else None, "yeni": b["metin"] if b else None,
                    "fark": word_diff(a["metin"] if a else "", b["metin"] if b else "")})
    return out


def write_diff(con, doc_key: str, eski_v, yeni_v, zaman: str | None = None) -> Path | None:
    """eski_v/yeni_v: versions satırları. Fark yoksa (yalnız biçim farkı) dosya yazılmaz."""
    doc = con.execute("SELECT * FROM documents WHERE doc_key=?", (doc_key,)).fetchone()
    birimler = compare(doc["kind"], doc["belge_id"], Path(eski_v["raw_path"]), Path(yeni_v["raw_path"]))
    if not birimler:
        return None
    zaman = zaman or datetime.now().isoformat(timespec="seconds")
    fark_id = f"{zaman.replace(':', '').replace('-', '')}_{doc_key.replace(':', '_')}_{eski_v['id']}-{yeni_v['id']}"
    body = {"fark_id": fark_id, "zaman": zaman, "doc_key": doc_key, "belge_id": doc["belge_id"], "tur": doc["kind"],
            "url": doc["url"],
            "eski": {"surum_id": eski_v["id"], "ilk_gorulme": eski_v["first_seen"], "hash": eski_v["content_hash"][:10]},
            "yeni": {"surum_id": yeni_v["id"], "ilk_gorulme": yeni_v["first_seen"], "hash": yeni_v["content_hash"][:10]},
            "ozet": {d: sum(b["durum"] == d for b in birimler) for d in ("degisti", "eklendi", "silindi")},
            "birimler": birimler}
    FARK_DIR.mkdir(parents=True, exist_ok=True)
    p = FARK_DIR / f"{fark_id}.json"
    p.write_text(json.dumps(body, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return p


def transitions(con, doc_key: str | None = None) -> list[tuple]:
    """checks tablosundaki sürüm geçişleri: (zaman, doc_key, eski_versions_satırı, yeni_versions_satırı)."""
    q = "SELECT * FROM checks WHERE result IN ('yeni_surum','eski_surume_dondu') AND detail LIKE '% -> %'"
    rows = con.execute(q + (" AND doc_key=?" if doc_key else "") + " ORDER BY checked_at",
                       (doc_key,) if doc_key else ()).fetchall()
    out = []
    for r in rows:
        a, b = (x.split("|")[0].strip() for x in r["detail"].split("->", 1))
        va = con.execute("SELECT * FROM versions WHERE doc_key=? AND content_hash LIKE ?", (r["doc_key"], a + "%")).fetchone()
        vb = con.execute("SELECT * FROM versions WHERE doc_key=? AND content_hash LIKE ?", (r["doc_key"], b + "%")).fetchone()
        if va and vb:
            out.append((r["checked_at"], r["doc_key"], va, vb))
    return out


def list_diffs(fark_dir: Path = FARK_DIR, limit: int = 50) -> list[dict]:
    out = []
    for p in sorted(fark_dir.glob("*.json"), reverse=True)[:limit]:
        d = json.loads(p.read_text(encoding="utf-8"))
        out.append({k: d[k] for k in ("fark_id", "zaman", "doc_key", "belge_id", "tur", "eski", "yeni", "ozet")}
                   | {"birimler": [{"birim": b["birim"], "etiket": b["etiket"], "durum": b["durum"]} for b in d["birimler"]]})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", default=None)
    ap.add_argument("--hepsi", action="store_true")
    args = ap.parse_args()
    if not (args.doc or args.hepsi):
        ap.error("--doc veya --hepsi")
    con = db.connect()
    for zaman, doc_key, va, vb in transitions(con, args.doc):
        p = write_diff(con, doc_key, va, vb, zaman)
        print(f"{zaman} {doc_key} {va['id']}->{vb['id']}: " + (str(p) if p else "içerik farkı yok (yalnız biçim)"))


if __name__ == "__main__":
    main()
