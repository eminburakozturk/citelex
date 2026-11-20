"""Resmî Gazete erken uyarı günlüğü: son N günü kontrol eder, yeni ilgili kayıtları jsonl'e yazar.

Kullanım:
  python -m src.update.erken_uyari
  python -m src.update.erken_uyari --gun-sayisi 7
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import httpx

from src.sources.http import FetchError, istemci
from src.sources.resmigazete import kontrol_et, load_sources

LOG_PATH = Path("logs/erken_uyari.jsonl")


def _seen_urls(log_path: Path) -> set[str]:
    if not log_path.exists():
        return set()
    urls: set[str] = set()
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        url = row.get("url")
        if url:
            urls.add(url)
    return urls


def kontrol_ve_kaydet(
    gun_sayisi: int = 3,
    log_path: Path = LOG_PATH,
    bugun: date | None = None,
    client: httpx.Client | None = None,
) -> list[dict]:
    """Son `gun_sayisi` günü kontrol eder; yeni ilgili kayıtları `log_path`'e ekler ve döndürür."""
    if gun_sayisi <= 0:
        raise ValueError("gun_sayisi pozitif bir tam sayı olmalı")

    log_path = Path(log_path)
    end_day = bugun or date.today()
    days = [end_day - timedelta(days=i) for i in range(gun_sayisi - 1, -1, -1)]
    seen = _seen_urls(log_path)
    sources = load_sources()
    yeni: list[dict] = []

    own_client = client is None
    cl = client or istemci()
    try:
        for d in days:
            try:
                records = kontrol_et(d, client=cl, sources=sources)
            except FetchError as exc:
                print(f"[HATA] {exc}", file=sys.stderr)
                continue

            for rec in records:
                if not rec.get("ilgili_belge_id"):
                    continue
                url = rec["url"]
                if url in seen:
                    continue
                entry = {
                    "zaman": datetime.now().isoformat(timespec="seconds"),
                    "gun": rec["tarih"],
                    "tur": rec["tur"],
                    "baslik": rec["baslik"],
                    "url": url,
                    "ilgili_belge_id": rec["ilgili_belge_id"],
                    "eslesme": rec.get("eslesme"),
                    "kanit": rec.get("kanit"),
                }
                log_path.parent.mkdir(parents=True, exist_ok=True)
                with log_path.open("a", encoding="utf-8") as fp:
                    fp.write(json.dumps(entry, ensure_ascii=False) + "\n")
                seen.add(url)
                yeni.append(entry)
    finally:
        if own_client:
            cl.close()

    return yeni


def main() -> int:
    ap = argparse.ArgumentParser(description="Resmî Gazete erken uyarı günlüğü")
    ap.add_argument("--gun-sayisi", type=int, default=3, help="Kontrol edilecek son N gün (varsayılan: 3)")
    ap.add_argument("--log", default=str(LOG_PATH), help="JSONL günlük dosya yolu")
    args = ap.parse_args()

    try:
        yeni = kontrol_ve_kaydet(gun_sayisi=args.gun_sayisi, log_path=Path(args.log))
    except ValueError as exc:
        print(f"[HATA] {exc}", file=sys.stderr)
        return 2

    print(f"Son {args.gun_sayisi} gün kontrol edildi: {len(yeni)} yeni ilgili kayıt ({args.log})")
    for r in yeni:
        print(f"  * [{r['gun']}] [{r['ilgili_belge_id']}|{r['eslesme']}] {r['baslik']} -> {r['url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
