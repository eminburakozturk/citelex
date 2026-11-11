"""KVKK Kurul karar özetleri (data/raw/kvkk_karar/*.txt) -> data/processed/chunks_karar.jsonl

Kaynak metin biçimi: src/sources/kvkk_extract.js çıktısı (BAŞLIK/KAYNAK/künye + paragraflar + "- " maddeleri).
Karar özetlerinde madde yapısı yok; dört bölüm var ve her bölüm "giriş cümlesi; + liste maddeleri + kapanış" biçiminde:
  sikayet        : ilgili kişinin iddiaları (metnin başı)
  savunma        : "...savunması talep edilmiş olup ... özetle;"
  degerlendirme  : "...inceleme neticesinde ... Kararı ile;"
  hukum          : "değerlendirmelerinden hareketle;" ... "karar verilmiştir."
Parça = bölüm; bölüm max_chars'ı aşarsa liste maddeleri gruplanır, her gruba giriş cümlesi tekrar eklenir (bağlam kaybı olmasın).
Şema src/ingest/chunk.py ile aynı alanlar (belge_tur="karar"; madde/fıkra alanları None) + kategori, url, karar_tarihi.

Kullanım: python -m src.ingest.parse_karar [--max-chars 1500]
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

RAW = Path("data/raw/kvkk_karar")
CFG = Path("configs/kvkk_kararlar.json")
OUT = Path("data/processed/chunks_karar.jsonl")

SECTION_START = [  # (bölüm, giriş satırı kalıbı) — sıra önemli, metin akışıyla aynı
    ("savunma", re.compile(r"(savunma|cevab[iî]|bilgi ve belge).*(özetle|;$)", re.I)),
    ("degerlendirme", re.compile(r"(inceleme|değerlendirme|incelenmesi) neticesinde|incelemede,? Kişisel Verileri Koruma Kurulu", re.I)),
    ("hukum", re.compile(r"değerlendirmelerinden hareketle|anlaşıldığından, veri sorumlusunun;|hususları dikkate alındığında", re.I)),
]
# Veri ihlali bildirimi kararlarında savunma bölümü yok: bildirim -> inceleme -> hüküm.
SECTION_LABEL = {"sikayet": "şikâyet veya ihlal bildirimi", "savunma": "veri sorumlusunun savunması",
                 "degerlendirme": "Kurulun değerlendirmesi", "hukum": "karar (hüküm)"}


def read_decision(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    meta, body = {}, []
    for l in lines:
        m = re.match(r"^(BAŞLIK|KAYNAK|Yayınlanma Tarihi|Karar Tarihi|Karar No|Konu Özeti): ?(.*)$", l)
        if m and m.group(1) not in meta:
            meta[m.group(1)] = m.group(2).strip()
        else:
            body.append(l)
    return {"meta": meta, "body": [l for l in body]}


def split_sections(body: list[str]) -> list[tuple[str, list[str]]]:
    """Satırları bölümlere ayır. Bölüm başlangıcı = liste dışı bir satırın kalıba uyması."""
    sections: list[tuple[str, list[str]]] = [("sikayet", [])]
    order = [s for s, _ in SECTION_START]
    for l in body:
        if l and not l.startswith("- "):
            cur = sections[-1][0]
            for sec, pat in SECTION_START:
                if order.index(sec) > (order.index(cur) if cur in order else -1) and pat.search(l):
                    sections.append((sec, []))
                    break
        sections[-1][1].append(l)
    return [(s, ls) for s, ls in sections if any(x.strip() for x in ls)]


def group_items(lines: list[str], max_chars: int) -> list[str]:
    """Bölümü parçalara böl: giriş paragrafı + maddeler; sınır aşılırsa maddeleri grupla."""
    paras: list[str] = []
    for l in lines:
        if not l.strip():
            continue
        if l.startswith("- ") or not paras or paras[-1].startswith("- "):
            paras.append(l)
        else:
            paras[-1] += "\n" + l
    total = sum(len(p) for p in paras)
    if total <= max_chars:
        return ["\n".join(paras)]
    intro = paras[0] if not paras[0].startswith("- ") else ""
    intro_short = intro if len(intro) <= 300 else intro[:300].rsplit(" ", 1)[0] + " …"
    chunks, cur, cur_len = [], [], 0
    items = paras[1:] if intro else paras
    for p in items:
        if cur and cur_len + len(p) > max_chars:
            chunks.append(cur)
            cur, cur_len = [], 0
        cur.append(p)
        cur_len += len(p)
    if cur:
        chunks.append(cur)
    return [("\n".join([intro] + c) if i == 0 and intro else "\n".join(([intro_short] if intro else []) + c))
            for i, c in enumerate(chunks)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-chars", type=int, default=1500)
    args = ap.parse_args()
    cfg = {k["dosya"].replace(".html", ".txt"): k for k in json.load(open(CFG, encoding="utf-8"))["kararlar"]}

    chunks, stats = [], Counter()
    missing_sections = []
    for path in sorted(RAW.glob("karar_*.txt")):
        info = cfg.get(path.name)
        if info is None:
            print(f"UYARI: {path.name} configs/kvkk_kararlar.json'da yok, atlandı")
            continue
        d = read_decision(path)
        no = d["meta"].get("Karar No", info["karar_no"])
        assert no == info["karar_no"], (path.name, no, info["karar_no"])
        belge_id = "kvkk-karar-" + no.replace("/", "-")
        secs = split_sections(d["body"])
        found = {s for s, _ in secs}
        if found != set(SECTION_LABEL):
            missing_sections.append((no, sorted(set(SECTION_LABEL) - found)))
        for sec, lines in secs:
            parts = group_items(lines, args.max_chars)
            for i, metin in enumerate(parts, 1):
                suffix = f"/{i}" if len(parts) > 1 else ""
                header = (f"KVKK Kurulu Kararı {no} ({d['meta'].get('Karar Tarihi', info['tarih'])}), "
                          f"konu: {info['konu']}, bölüm: {SECTION_LABEL[sec]}{suffix}")
                chunks.append({
                    "chunk_id": f"{belge_id}-{sec}-{i}",
                    "belge_id": belge_id, "belge_tur": "karar", "belge_no": no,
                    "belge_adi": d["meta"].get("BAŞLIK", ""),
                    "madde_tur": None, "madde_no": None, "fikra_no": None, "fikra_numara_kaynagi": None,
                    "baslik": info["konu"], "bolum": sec, "sayfa": None,
                    "atif": f"KVKK Kurulu K. {no}" + (f" ({SECTION_LABEL[sec]}{suffix})"),
                    "mulga": False, "diger_kanuna_islendi": False, "dipnotlar": [],
                    "kategori": info["kategori"], "url": info["url"],
                    "karar_tarihi": d["meta"].get("Karar Tarihi", info["tarih"]),
                    "metin": metin, "embed_text": header + "\n" + metin,
                })
                stats[sec] += 1

    ids = [c["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        for c in chunks:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    lens = sorted(len(c["metin"]) for c in chunks)
    n_dec = len({c["belge_id"] for c in chunks})
    print(f"{n_dec} karar -> {len(chunks)} parça -> {OUT}")
    print("bölüm:", dict(stats))
    print(f"karakter: medyan {lens[len(lens)//2]}, maks {lens[-1]}")
    if missing_sections:
        print("eksik bölüm:", missing_sections)


if __name__ == "__main__":
    main()
