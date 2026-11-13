"""Oracle yayın paketi: sunucuya kopyalanacak TEK arşiv (deploy/citelex_paket.tar.gz; git dışı).

İçerik:
  kod/            git archive HEAD (yalnız commit'lenmiş dosyalar; .env ve data/ GİRMEZ)
  snapshots/      Qdrant anlık görüntüleri: citelex_hibrit, citelex_genis (embedding yeniden üretilmez)
  web_out/        statik arayüz (NEXT_PUBLIC_API_URL=same-origin ile derlenir)
  store/          sürüm deposu + farklar (/degisiklikler ve "son kontrol" için; ham dosyalar girmez)
Gizli değer taraması: arşive girecek metin dosyalarında anahtar kalıbı bulunursa paket YAZILMAZ.

Kullanım (yerelde, Qdrant çalışırken):  python -m scripts.yayin_oracle
Sonra: scp deploy/citelex_paket.tar.gz ubuntu@<ip>:~   (ayrıntı deploy/oracle/README.md)
"""
from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import httpx

from src.config import QDRANT_URL

OUT = Path("deploy/citelex_paket.tar.gz")
KOLEKSIYONLAR = ["citelex_hibrit", "citelex_genis"]
GIZLI = re.compile(rb"sk-or-v1-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|hf_[A-Za-z0-9]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY")


def snapshot(client: httpx.Client, name: str, hedef: Path) -> Path:
    r = client.post(f"{QDRANT_URL}/collections/{name}/snapshots", timeout=600)
    r.raise_for_status()
    snap = r.json()["result"]["name"]
    p = hedef / f"{name}.snapshot"
    with client.stream("GET", f"{QDRANT_URL}/collections/{name}/snapshots/{snap}", timeout=600) as s:
        s.raise_for_status()
        with p.open("wb") as fh:
            for chunk in s.iter_bytes():
                fh.write(chunk)
    client.delete(f"{QDRANT_URL}/collections/{name}/snapshots/{snap}")   # yerel Qdrant'ta yer kaplamasın
    print(f"  {name}: {p.stat().st_size / 1e6:.0f} MB")
    return p


def main() -> int:
    tmp = Path("deploy/_paket")
    shutil.rmtree(tmp, ignore_errors=True)
    (tmp / "snapshots").mkdir(parents=True)
    print("1/4 Qdrant anlık görüntüleri")
    with httpx.Client() as c:
        snaps = [snapshot(c, n, tmp / "snapshots") for n in KOLEKSIYONLAR]
    print("2/4 statik arayüz (same-origin)")
    env = {**os.environ, "NEXT_PUBLIC_API_URL": "same-origin"}
    subprocess.run("npm --prefix web run build", shell=True, check=True, env=env, stdout=subprocess.DEVNULL)
    print("3/4 kod (git archive HEAD)")
    kod = subprocess.run(["git", "archive", "--format=tar", "HEAD"], check=True, capture_output=True).stdout
    print("4/4 arşiv + gizli değer taraması")
    with tarfile.open(fileobj=io.BytesIO(kod)) as t:
        for m in t.getmembers():
            if m.isfile() and GIZLI.search(t.extractfile(m).read()):
                print(f"DURDU: gizli değer kalıbı -> {m.name}")
                return 1
    for p in Path("web/out").rglob("*"):
        if p.is_file() and GIZLI.search(p.read_bytes()):
            print(f"DURDU: gizli değer kalıbı -> {p}")
            return 1
    OUT.parent.mkdir(exist_ok=True)
    with tarfile.open(OUT, "w:gz") as out:
        with tarfile.open(fileobj=io.BytesIO(kod)) as t:
            for m in t.getmembers():
                m.name = "citelex/" + m.name
                out.addfile(m, t.extractfile(m) if m.isfile() else None)
        out.add("web/out", arcname="citelex/web_out")
        for p in snaps:
            out.add(p, arcname=f"citelex/snapshots/{p.name}")
        store = Path("data/store")
        if (store / "citelex.db").exists():
            out.add(store / "citelex.db", arcname="citelex/store/citelex.db")
        if (store / "farklar").is_dir():
            out.add(store / "farklar", arcname="citelex/store/farklar")
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Paket: {OUT} ({OUT.stat().st_size / 1e6:.0f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
