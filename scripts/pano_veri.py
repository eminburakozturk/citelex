"""results/ altındaki değerlendirme çıktılarından web/public/pano.json üretir.

Girdiler (yalnız okunur):
  - results/eval_history.jsonl
  - results/eval_*.jsonl
  - results/sadakat_*__hakem_*.jsonl (varsa)

Çalıştırma:
  python scripts/pano_veri.py
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
OUT_PATH = ROOT / "web" / "public" / "pano.json"


def llm_tag(llm: str) -> str:
    return re.sub(r"[^a-z0-9.]+", "_", llm.lower())


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def calc_median_sure(rows: list[dict]) -> float | None:
    sures = sorted(r["sure_sn"] for r in rows if r.get("sure_sn") is not None and not r.get("hata"))
    if not sures:
        return None
    return round(float(sures[len(sures) // 2]), 2)


def load_sadakat(tag: str) -> tuple[dict | None, dict[str, bool | None]]:
    candidates = sorted(RESULTS_DIR.glob(f"sadakat_{tag}__hakem_*.jsonl"))
    if not candidates:
        return None, {}
    path = max(candidates, key=lambda p: p.stat().st_mtime)
    rows = [r for r in read_jsonl(path) if not r.get("hata")]
    if not rows:
        return None, {}

    cevap = len(rows)
    sadik_say = sum(1 for r in rows if r.get("sadik"))
    destekli = sum(int(r.get("destekli") or 0) for r in rows)
    kismen = sum(int(r.get("kismen") or 0) for r in rows)
    desteksiz = sum(int(r.get("desteksiz") or 0) for r in rows)
    n_iddia = sum(int(r.get("n_iddia") or 0) for r in rows)
    hakem = next((r.get("hakem_model") for r in rows if r.get("hakem_model")), None)

    ozet = {
        "hakem": hakem,
        "dosya": path.name,
        "cevap": cevap,
        "sadik": sadik_say,
        "sadik_orani": round(sadik_say / cevap, 4) if cevap else None,
        "destekli": destekli,
        "kismen": kismen,
        "desteksiz": desteksiz,
        "n_iddia": n_iddia,
        "destekli_orani": round(destekli / n_iddia, 4) if n_iddia else None,
    }
    by_id: dict[str, bool | None] = {r["id"]: r.get("sadik") for r in rows if "id" in r}
    return ozet, by_id


def build_pano() -> dict:
    history_raw = read_jsonl(RESULTS_DIR / "eval_history.jsonl")

    gecmis: list[dict] = []
    latest_tam: dict[str, dict] = {}
    for h in history_raw:
        n_ic = int(h.get("n_ic") or 0)
        n_dis = int(h.get("n_dis") or 0)
        dogru = int(h.get("dogru") or 0)
        entry = {
            "tarih": h.get("tarih"),
            "llm": h.get("llm"),
            "commit": h.get("commit"),
            "n_ic": n_ic,
            "n_dis": n_dis,
            "baglam": int(h.get("baglam") or 0),
            "atif": int(h.get("atif") or 0),
            "icerik": int(h.get("icerik") or 0),
            "dogru": dogru,
            "dogru_orani": round(dogru / n_ic, 4) if n_ic else None,
            "yanlis_ret": int(h.get("yanlis_ret") or 0),
            "dogru_ret": int(h.get("dogru_ret") or 0),
            "gecersiz_atif": int(h.get("gecersiz_atif") or 0),
            "hata": int(h.get("hata") or 0),
            "tam": bool(h.get("tam")),
        }
        gecmis.append(entry)
        if entry["tam"] and entry["llm"]:
            latest_tam[entry["llm"]] = entry

    modeller: list[dict] = []
    raw_by_llm: dict[str, dict[str, dict]] = {}
    sadakat_by_llm: dict[str, dict[str, bool | None]] = {}
    question_meta: dict[str, dict] = {}
    question_order: list[str] = []

    for llm, h in latest_tam.items():
        tag = llm_tag(llm)
        raw_path = RESULTS_DIR / f"eval_{tag}.jsonl"
        raw_rows = read_jsonl(raw_path)

        medyan_sure = calc_median_sure(raw_rows)
        sadakat_ozet, sadakat_map = load_sadakat(tag)
        sadakat_by_llm[llm] = sadakat_map

        row_map: dict[str, dict] = {}
        for r in raw_rows:
            qid = r.get("id")
            if not qid:
                continue
            row_map[qid] = r
            if qid not in question_meta:
                question_meta[qid] = {
                    "id": qid,
                    "tur": r.get("tur"),
                    "soru": r.get("soru"),
                }
                question_order.append(qid)
        raw_by_llm[llm] = row_map

        n_ic = h["n_ic"]
        n_dis = h["n_dis"]
        modeller.append(
            {
                "llm": llm,
                "tag": tag,
                "tarih": h["tarih"],
                "commit": h["commit"],
                "n_ic": n_ic,
                "n_dis": n_dis,
                "baglam": h["baglam"],
                "atif": h["atif"],
                "icerik": h["icerik"],
                "dogru": h["dogru"],
                "dogru_orani": round(h["dogru"] / n_ic, 4) if n_ic else None,
                "yanlis_ret": h["yanlis_ret"],
                "yanlis_ret_orani": round(h["yanlis_ret"] / n_ic, 4) if n_ic else None,
                "dogru_ret": h["dogru_ret"],
                "dogru_ret_orani": round(h["dogru_ret"] / n_dis, 4) if n_dis else None,
                "gecersiz_atif": h["gecersiz_atif"],
                "hata": h["hata"],
                "medyan_sure_sn": medyan_sure,
                "sadakat": sadakat_ozet,
            }
        )

    modeller.sort(
        key=lambda m: (
            -(m["dogru_orani"] or 0.0),
            m["medyan_sure_sn"] if m["medyan_sure_sn"] is not None else 9999.0,
        )
    )

    sorular: list[dict] = []
    for qid in question_order:
        meta = question_meta[qid]
        sonuclar: dict[str, dict] = {}
        for m in modeller:
            llm = m["llm"]
            r = raw_by_llm.get(llm, {}).get(qid)
            if not r:
                continue
            skor = r.get("skor") or {}
            if r.get("hata"):
                sonuclar[llm] = {
                    "dogru": False,
                    "hata": True,
                    "sure_sn": r.get("sure_sn"),
                }
            elif meta["tur"] == "kapsam_disi":
                sonuclar[llm] = {
                    "dogru": bool(skor.get("dogru_ret")),
                    "dogru_ret": bool(skor.get("dogru_ret")),
                    "katman": skor.get("katman"),
                    "sure_sn": r.get("sure_sn"),
                }
            else:
                sonuclar[llm] = {
                    "dogru": bool(skor.get("dogru")),
                    "baglam": bool(skor.get("baglam")),
                    "atif": bool(skor.get("atif")),
                    "icerik": bool(skor.get("icerik")),
                    "yanlis_ret": bool(skor.get("yanlis_ret")),
                    "katman": skor.get("katman"),
                    "sure_sn": r.get("sure_sn"),
                    "sadik": sadakat_by_llm.get(llm, {}).get(qid),
                }
        sorular.append({**meta, "sonuclar": sonuclar})

    return {
        "uretim_tarihi": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "modeller": modeller,
        "gecmis": gecmis,
        "sorular": sorular,
    }


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pano = build_pano()
    OUT_PATH.write_text(json.dumps(pano, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Yazıldı: {OUT_PATH} ({len(pano['modeller'])} model, {len(pano['gecmis'])} çalıştırma, {len(pano['sorular'])} soru)")


if __name__ == "__main__":
    main()
