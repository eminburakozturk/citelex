"""Citelex yayın duman testi (smoke test).

Kullanım:
    python scripts/duman_testi.py http://127.0.0.1:8000
    python -m scripts.duman_testi https://<alan-adi>
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from typing import Callable

SORU = "Yıllık izin kaç gündür?"
TAURI_ORIGIN = "http://tauri.localhost"
RATELIMIT_HEADERS = (
    "x-ratelimit-limit",
    "x-ratelimit-remaining",
    "x-ratelimit-reset",
    "ratelimit-limit",
    "ratelimit-remaining",
    "ratelimit-reset",
    "ratelimit",
    "retry-after",
)


def _http(
    url: str,
    *,
    method: str = "GET",
    body: dict | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 90.0,
) -> tuple[int, dict[str, str], bytes]:
    req_headers = dict(headers or {})
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            hdrs = {k.lower(): v for k, v in resp.headers.items()}
            return resp.status, hdrs, resp.read()
    except urllib.error.HTTPError as e:
        hdrs = {k.lower(): v for k, v in e.headers.items()} if e.headers else {}
        return e.code, hdrs, e.read()


def run_smoke(base_url: str) -> int:
    base = base_url.rstrip("/")
    results: list[tuple[str, bool, float, str]] = []
    sor_headers_cache: dict[str, str] = {}

    def check(ad: str, fn: Callable[[], tuple[bool, str]]) -> None:
        t0 = time.perf_counter()
        try:
            ok, detay = fn()
        except Exception as e:  # noqa: BLE001
            ok, detay = False, f"Hata: {type(e).__name__}: {e}"
        sure = time.perf_counter() - t0
        sembol = "✓" if ok else "✗"
        results.append((ad, ok, sure, detay))
        print(f"  {sembol} {ad:<42} ({sure:5.2f} sn) — {detay}")

    print(f"Citelex Duman Testi — Hedef: {base}\n")

    # 1. /saglik
    def c_saglik() -> tuple[bool, str]:
        code, _, raw = _http(f"{base}/saglik", timeout=15)
        d = json.loads(raw.decode("utf-8"))
        ok = code == 200 and d.get("durum") == "ok" and d.get("qdrant") == "ok" and (d.get("parca_sayisi") or 0) > 0
        return ok, f"HTTP {code}, durum={d.get('durum')}, qdrant={d.get('qdrant')}, parca={d.get('parca_sayisi')}"

    check("1. GET /saglik", c_saglik)

    # 2. /guncellik
    def c_guncellik() -> tuple[bool, str]:
        code, _, raw = _http(f"{base}/guncellik", timeout=15)
        d = json.loads(raw.decode("utf-8"))
        ok = (
            code == 200
            and isinstance(d, dict)
            and "son_kontrol" in d
            and "belge_sayisi" in d
            and isinstance(d.get("rg_bekleyen"), list)
        )
        return ok, f"HTTP {code}, son_kontrol={d.get('son_kontrol')}, belge_sayisi={d.get('belge_sayisi')}"

    check("2. GET /guncellik", c_guncellik)

    # 3. /kaynak?anahtar=is-kanunu:53
    def c_kaynak() -> tuple[bool, str]:
        code, _, raw = _http(f"{base}/kaynak?anahtar=is-kanunu:53", timeout=15)
        d = json.loads(raw.decode("utf-8"))
        gecmis = d.get("gecmis")
        iliskili = d.get("iliskili")
        ok = (
            code == 200
            and isinstance(gecmis, list)
            and len(gecmis) > 0
            and isinstance(iliskili, list)
            and len(iliskili) > 0
        )
        return ok, f"HTTP {code}, gecmis={len(gecmis or [])} kayıt, iliskili={len(iliskili or [])} kayıt"

    check("3. GET /kaynak?anahtar=is-kanunu:53", c_kaynak)

    # 4. /degisiklikler
    def c_degisiklikler() -> tuple[bool, str]:
        code, _, raw = _http(f"{base}/degisiklikler", timeout=15)
        d = json.loads(raw.decode("utf-8"))
        lst = d.get("degisiklikler")
        ok = code == 200 and isinstance(lst, list) and "son_kontrol" in d
        return ok, f"HTTP {code}, degisiklikler={len(lst or [])} kayıt"

    check("4. GET /degisiklikler", c_degisiklikler)

    # 5. Statik / ve /pano/
    def c_statik() -> tuple[bool, str]:
        c1, _, r1 = _http(f"{base}/", timeout=15)
        c2, _, r2 = _http(f"{base}/pano/", timeout=15)
        h1 = r1.decode("utf-8", errors="replace")
        h2 = r2.decode("utf-8", errors="replace")
        ok = c1 == 200 and c2 == 200 and "<html" in h1.lower() and "<html" in h2.lower()
        return ok, f"/ (HTTP {c1}, {len(r1)} B), /pano/ (HTTP {c2}, {len(r2)} B)"

    check("5. GET / ve GET /pano/ (statik)", c_statik)

    # 6. POST /sor?akis=false
    def c_sor_json() -> tuple[bool, str]:
        code, hdrs, raw = _http(f"{base}/sor?akis=false", method="POST", body={"soru": SORU}, timeout=120)
        sor_headers_cache.update(hdrs)
        d = json.loads(raw.decode("utf-8"))
        kaynaklar = d.get("kaynaklar")
        uyari = d.get("uyari")
        adimlar = d.get("adimlar")
        ok = (
            code == 200
            and not d.get("bilmiyorum")
            and isinstance(kaynaklar, list)
            and len(kaynaklar) > 0
            and isinstance(uyari, str)
            and len(uyari.strip()) > 0
            and isinstance(adimlar, list)
            and len(adimlar) > 0
        )
        return (
            ok,
            f"HTTP {code}, atıf={len(kaynaklar or [])}, uyari={'var' if uyari else 'yok'}, adimlar={len(adimlar or [])}",
        )

    check("6. POST /sor?akis=false", c_sor_json)

    # 7. POST /sor akışlı (SSE)
    def c_sor_sse() -> tuple[bool, str]:
        code, hdrs, raw = _http(f"{base}/sor", method="POST", body={"soru": SORU}, timeout=120)
        for k, v in hdrs.items():
            sor_headers_cache.setdefault(k, v)
        text = raw.decode("utf-8", errors="replace")
        events: list[tuple[str, str]] = []
        cur_event = None
        for line in text.splitlines():
            if line.startswith("event:"):
                cur_event = line.split(":", 1)[1].strip()
            elif line.startswith("data:") and cur_event is not None:
                events.append((cur_event, line.split(":", 1)[1].strip()))
                cur_event = None
        names = [e[0] for e in events]
        son_ok = False
        if names and names[-1] == "sonuc":
            son_veri = json.loads(events[-1][1])
            son_ok = bool(son_veri.get("kaynaklar")) and bool(son_veri.get("adimlar"))
        ok = code == 200 and "text/event-stream" in hdrs.get("content-type", "") and bool(names) and names[-1] == "sonuc" and son_ok
        ozet = " -> ".join(names[:3] + ([f"...({len(names)})", names[-1]] if len(names) > 4 else names[3:]))
        return ok, f"HTTP {code}, olaylar=[{ozet}]"

    check("7. POST /sor (SSE akışlı)", c_sor_sse)

    # 8. CORS başlığı (Origin: http://tauri.localhost)
    def c_cors() -> tuple[bool, str]:
        code, hdrs, _ = _http(
            f"{base}/saglik",
            headers={"Origin": TAURI_ORIGIN},
            timeout=15,
        )
        acao = hdrs.get("access-control-allow-origin")
        ok = code == 200 and acao in (TAURI_ORIGIN, "*")
        return ok, f"Origin={TAURI_ORIGIN} -> Access-Control-Allow-Origin={acao!r}"

    check("8. CORS başlığı (tauri.localhost)", c_cors)

    # 9. İstek sınırı başlığı
    def c_ratelimit() -> tuple[bool, str]:
        # BİLGİ: API sınırı yalnız 429 yanıtında Retry-After ile bildirir (tasarım kararı); 200'de başlık beklenmez.
        bulunan = {k: sor_headers_cache[k] for k in RATELIMIT_HEADERS if k in sor_headers_cache}
        detay = ", ".join(f"{k}={v}" for k, v in bulunan.items()) if bulunan else "200'de başlık yok (beklenen; sınır 429 + Retry-After ile bildirilir)"
        return True, "bilgi: " + detay

    check("9. İstek sınırı (bilgi)", c_ratelimit)

    gecen = sum(1 for _, ok, _, _ in results if ok)
    toplam = len(results)
    print(f"\nSonuç: {gecen}/{toplam} kontrol geçti.")
    return 0 if gecen == toplam else 1


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Citelex yayın duman testi.")
    p.add_argument("taban_url", nargs="?", default="http://127.0.0.1:8000", help="API taban adresi")
    args = p.parse_args()
    sys.exit(run_smoke(args.taban_url))


if __name__ == "__main__":
    main()
