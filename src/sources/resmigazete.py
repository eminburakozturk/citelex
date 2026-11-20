"""resmigazete.gov.tr günlük fihrist (erken uyarı): başlıkları ve ilgili metinleri derin katmanla eşleştir.

Günlük fihrist sayfasından (eskiler/YYYY/MM/YYYYMMDD.htm) mevzuat başlıklarını ayrıştırır;
configs/sources.json'daki derin katman belgeleriyle (kanun no veya belge adı) eşleşenleri işaretler.
Başlıkta eşleşme yoksa, tür "kanun" (veya başlığında "Değişiklik" geçen yönetmelik/karar) olan
kayıtların hedef sayfasını/PDF'ini indirip metinde "6698 sayılı", "4857 sayılı", "6331 sayılı"
atıflarını arar (torba kanun erken uyarısı).

Kullanım:
  python -m src.sources.resmigazete --gun 2026-11-12
  python -m src.sources.resmigazete --son 7
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urljoin

import httpx
import pdfplumber
from lxml import html as lhtml

from src.sources.http import FetchError, get, istemci

BASE = "https://www.resmigazete.gov.tr"
FIHRIST_URL = BASE + "/eskiler/{gun:%Y/%m/%Y%m%d}.htm"
DEFAULT_SOURCES = Path("configs/sources.json")

_WS = re.compile(r"[ \t\u00a0\r\n]+")
_LEAD_DASH = re.compile(r"^[\s\u00a0]*[–—-]+[\s\u00a0]*")
_CHARSET_RE = re.compile(r"charset\s*=\s*['\"]?([a-zA-Z0-9_-]+)", re.I)
_MADDE_RE = re.compile(r"\b(?:GEÇİCİ\s+MADDE|EK\s+MADDE|MADDE)\s+\d+(?:/[A-Z])?\b")

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


def _clip(text: str, max_len: int = 200) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def _extract_kanit(norm_text: str, match_start: int, match_end: int, max_len: int = 200) -> str:
    lookback = max(0, match_start - 1500)
    matches = list(_MADDE_RE.finditer(norm_text, lookback, match_start))
    if matches:
        madde_m = matches[-1]
        m_start = madde_m.start()
        if match_end - m_start <= max_len:
            return _clip(norm_text[m_start:], max_len)
        prefix = madde_m.group(0) + " ... "
        rem = max_len - len(prefix)
        ctx_start = max(m_start, match_start - max(20, rem // 3))
        return _clip(prefix + norm_text[ctx_start:], max_len)

    ctx_start = max(0, match_start - 50)
    return _clip(norm_text[ctx_start:], max_len)


def metin_eslesme_bul(
    metin: str,
    sources: list[dict] | None = None,
) -> tuple[str | None, str | None]:
    """Metinde '6698/4857/6331 sayılı' kanun atfı arar; (belge_id, kanit) döndürür."""
    if sources is None:
        sources = load_sources()
    kanun_map = {
        str(s["belge_no"]).strip(): s["belge_id"]
        for s in sources
        if s.get("belge_tur") == "kanun"
        and s.get("belge_id") != "is-kanunu-1475"
        and str(s.get("belge_no") or "").strip().isdigit()
    }
    if not kanun_map:
        return None, None

    norm_text = _norm(metin)
    nos = "|".join(re.escape(k) for k in kanun_map)
    pattern = re.compile(rf"\b({nos})\s+[sS][aA][yY][ıI][lL][ıI]\b")
    m = pattern.search(norm_text)
    if not m:
        return None, None
    return kanun_map[m.group(1)], _extract_kanit(norm_text, m.start(), m.end())


def _extract_response_text(resp: httpx.Response, url: str) -> str:
    ct = (resp.headers.get("content-type") or "").lower()
    is_pdf = "pdf" in ct or url.lower().split("?")[0].endswith(".pdf") or resp.content[:5] == b"%PDF-"
    if is_pdf:
        with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
            return "\n".join(pg.extract_text() or "" for pg in pdf.pages)

    html_text = _decode_html(resp)
    doc = lhtml.fromstring(html_text)
    for bad in doc.xpath("//script|//style"):
        bad.drop_tree()
    return doc.text_content()


def _metin_kontrol_gerekli(rec: dict) -> bool:
    if rec.get("ilgili_belge_id") is not None:
        return False
    tur = rec.get("tur")
    if tur == "kanun":
        return True
    if tur in ("yonetmelik", "karar") and "değişiklik" in _tr_lower(rec.get("baslik") or ""):
        return True
    return False


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
            bid = eslesme_bul(baslik, sources)
            items.append({
                "tarih": tarih_str,
                "tur": tur,
                "baslik": baslik,
                "url": urljoin(base_url, href),
                "ilgili_belge_id": bid,
                "eslesme": "baslik" if bid else None,
                "kanit": None,
            })

    return items


def kontrol_et(
    gun: date,
    client: httpx.Client | None = None,
    sources: list[dict] | None = None,
    metin_kontrol: bool = True,
) -> list[dict]:
    """Verilen tarihin Resmî Gazete fihristini çeker; gerekirse hedef metni de tarar."""
    if sources is None:
        sources = load_sources()
    url = FIHRIST_URL.format(gun=gun)
    own_client = client is None
    cl = client or istemci()
    try:
        try:
            resp = get(url, client=cl)
        except (FetchError, httpx.HTTPError) as exc:
            raise FetchError(f"Resmî Gazete fihristi alınamadı ({gun.isoformat()} - {url}): {exc}") from exc

        page_html = _decode_html(resp)
        records = parse_fihrist(page_html, gun, base_url=str(resp.url), sources=sources)
        if not metin_kontrol:
            return records

        for rec in records:
            if not _metin_kontrol_gerekli(rec):
                continue
            try:
                sub_resp = get(rec["url"], client=cl)
                body_text = _extract_response_text(sub_resp, rec["url"])
            except Exception as exc:
                rec["metin_hatasi"] = str(exc)
                continue
            bid, kanit = metin_eslesme_bul(body_text, sources)
            if bid:
                rec["ilgili_belge_id"] = bid
                rec["eslesme"] = "metin"
                rec["kanit"] = kanit
        return records
    finally:
        if own_client:
            cl.close()


def _format_summary(records: list[dict], gun: date) -> str:
    ilgili = [r for r in records if r["ilgili_belge_id"]]
    hatalar = [r for r in records if r.get("metin_hatasi")]
    lines = [f"[{gun.isoformat()}] {len(records)} kayıt, {len(ilgili)} ilgili"]
    for r in ilgili:
        esl = r.get("eslesme") or "?"
        lines.append(f"  * [{r['ilgili_belge_id']}|{esl}] ({r['tur']}) {r['baslik']} -> {r['url']}")
        if r.get("kanit"):
            lines.append(f"    kanit: {r['kanit']}")
    for r in hatalar:
        lines.append(f"  ! [METİN HATASI] {r['baslik']} ({r['url']}): {r['metin_hatasi']}")
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
    t0 = time.monotonic()

    with istemci() as cl:
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

    elapsed = time.monotonic() - t0
    print(
        f"Toplam: {len(days) - errors}/{len(days)} gün başarılı, {total} kayıt, "
        f"{total_ilgili} ilgili, {errors} hata ({elapsed:.1f} sn)"
    )
    return 1 if errors and errors == len(days) else 0


if __name__ == "__main__":
    raise SystemExit(main())
