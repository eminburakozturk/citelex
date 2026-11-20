"""kvkk.gov.tr Kurul karar özeti: HTML -> gürültüsüz metin.

src/sources/kvkk_extract.js'in Python karşılığı; çıktısı onunla AYNI olmalı (data/raw/kvkk_karar/*.txt
tarayıcıyla üretildi; tests: python -m src.sources.kvkk --dogrula).
İçerik kabı .news__detail-article; eski sayfalarda içerik DIV sarmalayıcıda -> özyinelemeli inilir.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import httpx
from lxml import html as lhtml

from src.sources.http import get, istemci

BASE = "https://www.kvkk.gov.tr"
_WS = re.compile(r"[ \t \r\n]+")
_SEPS = re.compile(r"\s*:\s*")


def norm(s: str) -> str:
    return _WS.sub(" ", s).strip()


def _text(el) -> str:
    return norm(el.text_content())


def extract(page_html: str, url_path: str) -> str | None:
    doc = lhtml.fromstring(page_html)
    arts = doc.cssselect(".news__detail-article")
    if not arts:
        return None
    heads = doc.cssselect(".news__detail-head")
    out: list[str] = []
    title = ""

    def walk(el) -> None:
        nonlocal title
        for c in el:
            if not isinstance(c.tag, str):
                continue
            tg = c.tag.upper()
            if tg == "H2" and not title:
                title = _text(c)
            elif tg == "TABLE":
                for tr in c.iter("tr"):
                    cells = [_text(x) for x in tr if isinstance(x.tag, str)]
                    out.append(_SEPS.sub(": ", " ".join(x for x in cells if x), count=1))
                out.append("")
            elif tg in ("UL", "OL"):
                for li in c:
                    if isinstance(li.tag, str) and li.tag.upper() == "LI":
                        out.append("- " + _text(li))
                out.append("")
            elif tg in ("DIV", "SECTION", "ARTICLE") and c.cssselect("p, table, ul, ol, div"):
                walk(c)
            else:
                t = _text(c)
                if t:
                    out.extend([t, ""])

    walk(arts[0])
    lines = [f"BAŞLIK: {title}", f"KAYNAK: {BASE}{url_path}", _text(heads[0]) if heads else "", "", *out]
    txt = "\n".join(lines)
    txt = re.sub(r"\n{3,}", "\n\n", txt).strip() + "\n"
    return txt


def fetch_decision(url: str, client: httpx.Client | None = None) -> str | None:
    path = url.replace(BASE, "")
    r = get(url, client=client)
    return extract(r.text, path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dogrula", action="store_true", help="40 kararı indir, tarayıcı çıktısıyla karşılaştır")
    args = ap.parse_args()
    if not args.dogrula:
        ap.print_help()
        return
    cfg = json.load(open("configs/kvkk_kararlar.json", encoding="utf-8"))["kararlar"]
    same = diff = 0
    with istemci() as cl:
        for k in cfg:
            local = Path("data/raw/kvkk_karar") / k["dosya"].replace(".html", ".txt")
            got = fetch_decision(k["url"], cl)
            ref = local.read_text(encoding="utf-8")
            if got == ref:
                same += 1
            else:
                diff += 1
                a, b = (got or "").splitlines(), ref.splitlines()
                i = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
                print(f"FARK {k['karar_no']} satır {i}: py={a[i][:90] if i < len(a) else None!r} js={b[i][:90] if i < len(b) else None!r}")
    print(f"{same} aynı, {diff} farklı")


if __name__ == "__main__":
    main()
