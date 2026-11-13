"""resmigazete.gov.tr günlük fihrist (erken uyarı): başlıkları çek ve derin katmanla eşleştir.

Günlük fihrist sayfasından (eskiler/YYYY/MM/YYYYMMDD.htm) mevzuat başlıklarını ayrıştırır;
configs/sources.json'daki derin katman belgeleriyle (kanun no veya belge adı) eşleşenleri işaretler.
Her istekten önce src/sources/http.py üzerinden robots.txt ve hız sınırı uygulanır.

Kullanım:
  python -m src.sources.resmigazete --gun 2026-11-12
  python -m src.sources.resmigazete --son 7
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urljoin

import httpx
from lxml import html as lhtml

from src.sources.http import FetchError, get

BASE = "https://www.resmigazete.gov.tr"
FIHRIST_URL = BASE + "/eskiler/{gun:%Y/%m/%Y%m%d}.htm"
DEFAULT_SOURCES = Path("configs/sources.json")

_WS = re.compile(r"[ \t\u00a0\r\n]+")
_LEAD_DASH = re.compile(r"^[\s\u00a0]*[–—-]+[\s\u00a0]*")
_CHARSET_RE = re.compile(r"charset\s*=\s*['\"]?([a-zA-Z0-9_-]+)", re.I)

_BOLUM_BASLIKLARI = (
    "yasama bölümü",
    "yürütme ve idare bölümü",
    "yargı bölümü",
    "mevzuat",
)


def _tr_lower(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()


def _norm(s: str) -> str:
    return _WS.sub(" ", s).strip()


def _clean_title(s: str) -> str:
    return _LEAD_DASH.sub("", _norm(s)).strip()


def _decode_html(resp: httpx.Response) -> str:
    ct = resp.headers.get("content-type", "")
    m = _CHARSET_RE.search(ct) or _CHARSET_RE.search(resp.content[:4096].decode("ascii", errors="ignore"))
    if m:
        return resp.content.decode(m.group(1), errors="replace")
    try:
        return resp.content.decode("utf-8")
    except UnicodeDecodeError:
        return resp.content.decode("windows-1254", errors="replace")


def _heading_to_tur(heading: str) -> str:
    h = _tr_lower(_norm(heading))
    if "kanun" in h and "kararname" not in h:
        return "kanun"
    if "kararname" in h:
        return "kararname"
    if "yönetmelik" in h:
        return "yonetmelik"
    if "tebliğ" in h:
        return "teblig"
    if "genelge" in h:
        return "genelge"
    if "karar" in h:
        return "karar"
    if "tezkere" in h or "vekâlet" in h or "vekalet" in h:
        return "tezkere"
    return "diger"


def load_sources(path: Path = DEFAULT_SOURCES) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        v for k, v in data.items()
        if not k.startswith("_") and isinstance(v, dict) and "belge_id" in v
    ]


def eslesme_bul(baslik: str, sources: list[dict] | None = None) -> str | None:
    """Başlıkta derin katman belgesinin adı veya kanun numarası geçiyorsa belge_id döndür."""
    if sources is None:
        sources = load_sources()
    norm_title = _tr_lower(_norm(baslik))

    # Uzun/özgül belge adlarını önce dene; böylece yönetmelik adı genel "İş Kanunu"ndan önce yakalanır.
    by_name = sorted(
        (s for s in sources if s.get("belge_adi") and s.get("belge_id") != "is-kanunu-1475"),
        key=lambda s: len(s["belge_adi"]),
        reverse=True,
    )
    for src in by_name:
        adi = _tr_lower(_norm(src["belge_adi"]))
        if adi == "iş kanunu":
            if re.search(r"(?<!deniz\s)(?<!basın\s)\biş kanunu", norm_title):
                return src["belge_id"]
        elif adi in norm_title:
            return src["belge_id"]

    for src in sources:
        if src.get("belge_tur") != "kanun":
            continue
        no = str(src.get("belge_no") or "").strip()
        if not no:
            continue
        if src.get("belge_id") == "is-kanunu-1475" and "kanun" not in norm_title:
            continue
        if re.search(rf"\b{re.escape(no)}\b", norm_title):
            return src["belge_id"]

    return None


def parse_fihrist(
    page_html: str,
    gun: date,
    base_url: str | None = None,
    sources: list[dict] | None = None,
) -> list[dict]:
    """Resmî Gazete günlük fihrist HTML'ini ayrıştırıp kayıt listesi döndürür."""
    if sources is None:
        sources = load_sources()
    if base_url is None:
        base_url = FIHRIST_URL.format(gun=gun)

    doc = lhtml.fromstring(page_html)
    tarih_str = gun.isoformat()
    cur_tur: str | None = None
    items: list[dict] = []

    for p in doc.cssselect("p"):
        raw_text = _norm(p.text_content())
        if not raw_text:
            continue
        low = _tr_lower(raw_text)

        if low.startswith("ilân bölümü") or low.startswith("ilan bölümü"):
            break
        if "resmî gazete'nin kurumsal mobil" in low or "sayılı resmî gazete" in low:
            continue
        if low in _BOLUM_BASLIKLARI:
            cur_tur = None
            continue

        links = [a for a in p.cssselect("a") if a.get("href")]
        if not links:
            inferred = _heading_to_tur(raw_text)
            if inferred != "diger" or p.cssselect("u, b, strong"):
                cur_tur = inferred
            continue

        for a in links:
            href = (a.get("href") or "").strip()
            link_text = _clean_title(a.text_content())
            if not href or not link_text:
                continue
            baslik = _clean_title(raw_text) if len(links) == 1 else link_text
            tur = cur_tur if cur_tur and cur_tur != "diger" else _heading_to_tur(baslik)
            items.append({
                "tarih": tarih_str,
                "tur": tur,
                "baslik": baslik,
                "url": urljoin(base_url, href),
                "ilgili_belge_id": eslesme_bul(baslik, sources),
            })

    return items


def kontrol_et(
    gun: date,
    client: httpx.Client | None = None,
    sources: list[dict] | None = None,
) -> list[dict]:
    """Verilen tarihin Resmî Gazete fihristini çeker ve başlıkları döndürür."""
    url = FIHRIST_URL.format(gun=gun)
    try:
        resp = get(url, client=client)
    except (FetchError, httpx.HTTPError) as exc:
        raise FetchError(f"Resmî Gazete fihristi alınamadı ({gun.isoformat()} - {url}): {exc}") from exc

    page_html = _decode_html(resp)
    return parse_fihrist(page_html, gun, base_url=str(resp.url), sources=sources)


def _format_summary(records: list[dict], gun: date) -> str:
    ilgili = [r for r in records if r["ilgili_belge_id"]]
    lines = [f"[{gun.isoformat()}] {len(records)} kayıt, {len(ilgili)} ilgili"]
    for r in ilgili:
        lines.append(f"  * [{r['ilgili_belge_id']}] ({r['tur']}) {r['baslik']} -> {r['url']}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Resmî Gazete günlük fihrist erken uyarı kontrolü")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--gun", help="Tek gün (YYYY-AA-GG)")
    grp.add_argument("--son", type=int, help="Bugün dahil son N gün")
    args = ap.parse_args()

    if args.gun:
        try:
            days = [date.fromisoformat(args.gun)]
        except ValueError as exc:
            print(f"[HATA] Geçersiz tarih biçimi ({args.gun}): {exc}", file=sys.stderr)
            return 2
    else:
        if args.son <= 0:
            print("[HATA] --son pozitif bir tam sayı olmalı", file=sys.stderr)
            return 2
        today = date.today()
        days = [today - timedelta(days=i) for i in range(args.son - 1, -1, -1)]

    sources = load_sources()
    total = 0
    total_ilgili = 0
    errors = 0

    with httpx.Client() as cl:
        for d in days:
            try:
                recs = kontrol_et(d, client=cl, sources=sources)
            except FetchError as exc:
                errors += 1
                print(f"[HATA] {exc}", file=sys.stderr)
                continue
            total += len(recs)
            total_ilgili += sum(1 for r in recs if r["ilgili_belge_id"])
            print(_format_summary(recs, d))

    print(f"Toplam: {len(days) - errors}/{len(days)} gün başarılı, {total} kayıt, {total_ilgili} ilgili, {errors} hata")
    return 1 if errors and errors == len(days) else 0


if __name__ == "__main__":
    raise SystemExit(main())
