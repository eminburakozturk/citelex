"""Kaynak sitelere nazik HTTP istemcisi (PLAN.md scraping kuralları).

- Tanımlayıcı User-Agent; tarayıcı taklidi YOK.
- Aynı host'a istekler arası en az MIN_DELAY saniye.
- Geçici hatada (5xx, zaman aşımı) 2 yeniden deneme; 4xx'te deneme yok.
- robots.txt host başına bir kez okunur; izin vermeyen yol istenmez.
"""
from __future__ import annotations

import time
import urllib.robotparser
from urllib.parse import urlsplit

import httpx

USER_AGENT = "citelex/0.1 (mevzuat RAG arastirma prototipi; gunluk guncelleme kontrolu)"
MIN_DELAY = 2.0
_last: dict[str, float] = {}
_robots: dict[str, urllib.robotparser.RobotFileParser] = {}


class FetchError(RuntimeError):
    pass


def _allowed(url: str, client: httpx.Client) -> bool:
    host = "{0.scheme}://{0.netloc}".format(urlsplit(url))
    if host not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            r = client.get(host + "/robots.txt", headers={"User-Agent": USER_AGENT}, timeout=20)
            rp.parse(r.text.splitlines() if r.status_code == 200 else [])
        except httpx.HTTPError:
            rp.parse([])
        _robots[host] = rp
    return _robots[host].can_fetch(USER_AGENT, url)


def get(url: str, client: httpx.Client | None = None, timeout: float = 60) -> httpx.Response:
    own = client is None
    client = client or httpx.Client()
    try:
        if not _allowed(url, client):
            raise FetchError(f"robots.txt izin vermiyor: {url}")
        host = urlsplit(url).netloc
        last_exc: Exception | None = None
        for attempt in range(3):
            wait = MIN_DELAY - (time.time() - _last.get(host, 0))
            if wait > 0:
                time.sleep(wait)
            try:
                r = client.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout, follow_redirects=True)
                _last[host] = time.time()
            except httpx.TimeoutException as e:
                _last[host] = time.time()
                last_exc = e
                time.sleep(5 * (attempt + 1))
                continue
            if r.status_code >= 500:
                last_exc = FetchError(f"{r.status_code} {url}")
                time.sleep(5 * (attempt + 1))
                continue
            if r.status_code != 200:
                raise FetchError(f"{r.status_code} {url}")
            return r
        raise FetchError(f"3 denemede alınamadı: {url} ({last_exc})")
    finally:
        if own:
            client.close()
