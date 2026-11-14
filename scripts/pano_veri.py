"""results/ altındaki değerlendirme çıktılarından web/public/pano.json üretir.

Girdiler (yalnız okunur):
  - results/eval_history.jsonl
  - results/eval_*.jsonl
  - results/sadakat_*__hakem_*.jsonl (varsa)
  - results/rerank_compare.md (varsa)
  - results/genis_check.md ve results/eval_*_genis.md (varsa)

Çalıştırma:
  python scripts/pano_veri.py
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
OUT_PATH = ROOT / "web" / "public" / "pano.json"


def llm_tag(llm: str) -> str:
    return re.sub(r"[^a-z0-9.]+", "_", llm.lower())


def config_info(rerank: bool, ajan: bool, genis: bool = False) -> tuple[str, str, str]:
    if rerank and ajan:
        kod, ad, suffix = "reranker+ajan", "reranker + ajan", "_ajan_rerank"
    elif rerank:
        kod, ad, suffix = "reranker", "reranker", "_rerank"
    elif ajan:
        kod, ad, suffix = "ajan", "ajan", "_ajan"
    else:
        kod, ad, suffix = "tek_adim", "tek adım", ""
    if genis:
        kod += "+genis"
        ad += " + geniş"
        suffix += "_genis"
    return kod, ad, suffix


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


def tag_candidates(base_tag: str, rerank: bool, ajan: bool, genis: bool = False) -> list[str]:
    if rerank and ajan:
        combos = ["_ajan_rerank", "_rerank_ajan"]
    elif rerank:
        combos = ["_rerank"]
    elif ajan:
        combos = ["_ajan"]
    else:
        combos = [""]
    if not genis:
        return [f"{base_tag}{c}" for c in combos]
    out: list[str] = []
    for c in combos:
        out.append(f"{base_tag}{c}_genis")
        if c:
            out.append(f"{base_tag}_genis{c}")
    return out


def find_raw_eval(base_tag: str, rerank: bool, ajan: bool, genis: bool = False) -> Path | None:
    candidates = [RESULTS_DIR / f"eval_{t}.jsonl" for t in tag_candidates(base_tag, rerank, ajan, genis)]
    if ajan and not rerank:
        gsuf = "_genis" if genis else ""
        candidates.extend(sorted(RESULTS_DIR.glob(f"eval_{base_tag}_ajan*{gsuf}.jsonl")))
    for p in candidates:
        if p.is_file():
            return p
    return None


def calc_median_sure(rows: list[dict]) -> float | None:
    sures = sorted(r["sure_sn"] for r in rows if r.get("sure_sn") is not None and not r.get("hata"))
    if not sures:
        return None
    return round(float(sures[len(sures) // 2]), 2)


def calc_yanlis_ret_katmanlari(rows: list[dict]) -> dict[str, int]:
    say = Counter()
    for r in rows:
        if r.get("hata") or r.get("tur") == "kapsam_disi":
            continue
        skor = r.get("skor") or {}
        if skor.get("yanlis_ret"):
            katman = skor.get("katman") or "belirsiz"
            say[katman] += 1
    return dict(say)


def load_sadakat(sadakat_tags: str | list[str]) -> tuple[dict | None, dict[str, bool | None]]:
    tags = [sadakat_tags] if isinstance(sadakat_tags, str) else list(sadakat_tags)
    candidates: list[Path] = []
    for tag in tags:
        candidates.extend(RESULTS_DIR.glob(f"sadakat_{tag}__hakem_*.jsonl"))
    candidates = sorted(set(candidates))
    if not candidates:
        return None, {}
    path = max(candidates, key=lambda p: p.stat().st_mtime)
    rows = [r for r in read_jsonl(path) if not r.get("hata")]
    if not rows:
        return None, {}

    cevap = len(rows)
    sadik_say = sum(1 for r in rows if r.get("sadik"))
    tam_destekli_say = sum(
        1
        for r in rows
        if int(r.get("kismen") or 0) == 0
        and int(r.get("desteksiz") or 0) == 0
        and int(r.get("n_iddia") or 0) > 0
    )
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
        "tam_destekli": tam_destekli_say,
        "tam_destekli_orani": round(tam_destekli_say / cevap, 4) if cevap else None,
        "destekli": destekli,
        "kismen": kismen,
        "desteksiz": desteksiz,
        "n_iddia": n_iddia,
        "destekli_orani": round(destekli / n_iddia, 4) if n_iddia else None,
    }
    by_id: dict[str, bool | None] = {
        r["id"]: (
            int(r.get("kismen") or 0) == 0
            and int(r.get("desteksiz") or 0) == 0
            and int(r.get("n_iddia") or 0) > 0
        )
        for r in rows
        if "id" in r
    }
    return ozet, by_id


def parse_rerank_compare() -> dict | None:
    path = RESULTS_DIR / "rerank_compare.md"
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    satirlar: list[dict] = []
    in_table = False
    sure_notu: str | None = None
    for line in lines:
        s = line.strip()
        if s.startswith("| Kanal | Yöntem |"):
            in_table = True
            continue
        if in_table:
            if s.startswith("|---"):
                continue
            if not s.startswith("|"):
                in_table = False
            else:
                parts = [p.strip() for p in s.strip("|").split("|")]
                if len(parts) >= 7:
                    satirlar.append(
                        {
                            "kanal": parts[0],
                            "yontem": parts[1],
                            "n": int(parts[2]),
                            "r1": int(parts[3]),
                            "r3": int(parts[4]),
                            "r5": int(parts[5]),
                            "mrr": float(parts[6]),
                        }
                    )
        if s.startswith("Rerank süresi:"):
            sure_notu = s
    if not satirlar:
        return None
    return {"dosya": path.name, "satirlar": satirlar, "not": sure_notu}


def parse_compare_retrieval() -> dict | None:
    path = RESULTS_DIR / "compare_retrieval.md"
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    ozet_not: str | None = None
    sozcuksel_not: str | None = None
    parcalama_yontem: list[dict] = []
    sozcuksel: list[dict] = []
    bolum = 0
    in_table = False

    for line in lines:
        s = line.strip()
        if s.startswith("Sorular:"):
            ozet_not = s
            continue
        if s.startswith("## 1."):
            bolum = 1
            in_table = False
            continue
        if s.startswith("## 2."):
            bolum = 2
            in_table = False
            continue
        if bolum == 2 and not in_table and s and not s.startswith("|") and not s.startswith("#"):
            sozcuksel_not = s
            continue
        if s.startswith("| Parçalama | Yöntem |") or s.startswith("| Yöntem | R@1 |"):
            in_table = True
            continue
        if in_table:
            if s.startswith("|---"):
                continue
            if not s.startswith("|"):
                in_table = False
                continue
            parts = [p.strip() for p in s.strip("|").split("|")]
            if bolum == 1 and len(parts) >= 8:
                parcalama_yontem.append(
                    {
                        "parcalama": parts[0],
                        "yontem": parts[1],
                        "mevzuat_r1": parts[2],
                        "mevzuat_r5": parts[3],
                        "mevzuat_mrr": float(parts[4]),
                        "karar_r1": parts[5],
                        "karar_r3": parts[6],
                        "sure_sn": float(parts[7]),
                    }
                )
            elif bolum == 2 and len(parts) >= 4:
                sozcuksel.append(
                    {
                        "yontem": parts[0],
                        "r1": parts[1],
                        "r5": parts[2],
                        "mrr5": float(parts[3]),
                    }
                )

    if not parcalama_yontem and not sozcuksel:
        return None
    return {
        "dosya": path.name,
        "ozet_not": ozet_not,
        "parcalama_yontem": parcalama_yontem,
        "sozcuksel_not": sozcuksel_not,
        "sozcuksel": sozcuksel,
    }


def parse_genis_check() -> dict | None:
    path = RESULTS_DIR / "genis_check.md"
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    aciklama: str | None = None
    ozet: list[dict] = []
    sorular: list[dict] = []
    tablo = 0

    for line in lines:
        s = line.strip()
        if s.startswith("Eşik "):
            aciklama = s
            continue
        if s.startswith("| Ölçüt | Değer |"):
            tablo = 1
            continue
        if s.startswith("| # | Soru |"):
            tablo = 2
            continue
        if s.startswith("|---"):
            continue
        if not s.startswith("|"):
            if tablo in (1, 2):
                tablo = 0
            continue
        parts = [p.strip() for p in s.strip("|").split("|")]
        if tablo == 1 and len(parts) >= 2:
            ozet.append({"olcut": parts[0], "deger": parts[1]})
        elif tablo == 2 and len(parts) >= 7:
            sorular.append(
                {
                    "id": parts[0],
                    "soru": parts[1],
                    "beklenen": parts[2],
                    "kanal": parts[3],
                    "baglamda": parts[4] == "✓",
                    "sira": parts[5],
                    "ilk3": parts[6],
                }
            )

    if not ozet and not sorular:
        return None
    return {
        "dosya": path.name,
        "taslak": True,
        "not": aciklama,
        "ozet": ozet,
        "sorular": sorular,
    }


def _genis_tag_candidates(stem_tag: str) -> list[str]:
    if not stem_tag.endswith("_genis"):
        return [stem_tag]
    core = stem_tag.removesuffix("_genis")
    if core.endswith("_rerank_ajan"):
        base = core.removesuffix("_rerank_ajan")
        return tag_candidates(base, True, True, True)
    if core.endswith("_ajan_rerank"):
        base = core.removesuffix("_ajan_rerank")
        return tag_candidates(base, True, True, True)
    if core.endswith("_rerank"):
        base = core.removesuffix("_rerank")
        return tag_candidates(base, True, False, True)
    if core.endswith("_ajan"):
        base = core.removesuffix("_ajan")
        return tag_candidates(base, False, True, True)
    return [stem_tag]


def parse_genis_evals() -> list[dict]:
    sonuclar: list[dict] = []
    for path in sorted(RESULTS_DIR.glob("eval_*_genis.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        model: str | None = None
        bilgi: str | None = None
        taslak_not: str | None = None
        olcutler: list[dict] = []
        kapsam_disi: str | None = None
        diger: str | None = None
        notlar: list[dict] = []
        tablo = 0

        for line in lines:
            s = line.strip()
            if s.startswith("# Değerlendirme — "):
                model = s.removeprefix("# Değerlendirme — ").strip()
                continue
            if s.startswith("Tarih: "):
                bilgi = s
                continue
            if s.startswith("Beklenen cevaplar "):
                taslak_not = s
                continue
            if s.startswith("| Ölçüt | Tümü |"):
                tablo = 1
                continue
            if s.startswith("| # | Soru |"):
                tablo = 2
                continue
            if s.startswith("Doğru \"bilmiyorum\":"):
                kapsam_disi = s.removeprefix("Doğru \"bilmiyorum\":").strip()
                continue
            if s.startswith("Geçersiz atıf "):
                diger = s
                continue
            if s.startswith("|---"):
                continue
            if not s.startswith("|"):
                if tablo in (1, 2):
                    tablo = 0
                continue
            parts = [p.strip() for p in s.strip("|").split("|")]
            if tablo == 1 and len(parts) >= 4:
                olcutler.append(
                    {
                        "olcut": parts[0].replace("**", ""),
                        "tumu": parts[1],
                        "mevzuat": parts[2],
                        "karar": parts[3],
                    }
                )
            elif tablo == 2 and len(parts) >= 6:
                notlar.append(
                    {
                        "id": parts[0],
                        "soru": parts[1],
                        "baglam": parts[2],
                        "atif": parts[3],
                        "icerik": parts[4],
                        "not": parts[5],
                    }
                )

        if olcutler:
            sadakat_ozet, _ = load_sadakat(_genis_tag_candidates(path.stem.removeprefix("eval_")))
            sonuclar.append(
                {
                    "dosya": path.name,
                    "model": model,
                    "bilgi": bilgi,
                    "taslak_not": taslak_not,
                    "olcutler": olcutler,
                    "kapsam_disi": kapsam_disi,
                    "diger": diger,
                    "sadakat": sadakat_ozet,
                    "basarisizlar": notlar,
                }
            )
    return sonuclar


def build_pano() -> dict:
    history_raw = read_jsonl(RESULTS_DIR / "eval_history.jsonl")

    gecmis: list[dict] = []
    latest_tam: dict[str, dict] = {}
    for h in history_raw:
        if not h.get("tam"):
            continue
        llm = h.get("llm")
        if not llm:
            continue
        rerank = bool(h.get("rerank"))
        ajan = bool(h.get("ajan"))
        genis = bool(h.get("genis"))
        yap_kod, yap_ad, _ = config_info(rerank, ajan, genis)
        anahtar = f"{llm}|{yap_kod}"

        n_ic = int(h.get("n_ic") or 0)
        n_dis = int(h.get("n_dis") or 0)
        dogru = int(h.get("dogru") or 0)
        entry = {
            "anahtar": anahtar,
            "tarih": h.get("tarih"),
            "llm": llm,
            "yapilandirma": yap_kod,
            "yapilandirma_adi": yap_ad,
            "rerank": rerank,
            "ajan": ajan,
            "genis": genis,
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
            "tam": True,
        }
        gecmis.append(entry)
        # Geniş katmanlı yapılandırmalar da tabloya girer: yayındaki yapılandırma "ajan + geniş"tir.
        latest_tam[anahtar] = entry

    modeller: list[dict] = []
    raw_by_key: dict[str, dict[str, dict]] = {}
    sadakat_by_key: dict[str, dict[str, bool | None]] = {}
    question_meta: dict[str, dict] = {}
    question_order: list[str] = []

    for anahtar, h in latest_tam.items():
        llm = h["llm"]
        rerank = h["rerank"]
        ajan = h["ajan"]
        genis = h["genis"]
        _, _, suffix = config_info(rerank, ajan, genis)
        base_tag = llm_tag(llm)
        full_tag = base_tag + suffix

        raw_path = find_raw_eval(base_tag, rerank, ajan, genis)
        raw_rows = read_jsonl(raw_path) if raw_path else []

        medyan_sure = calc_median_sure(raw_rows)
        yanlis_ret_katmanlari = calc_yanlis_ret_katmanlari(raw_rows)
        sadakat_ozet, sadakat_map = load_sadakat(tag_candidates(base_tag, rerank, ajan, genis))
        sadakat_by_key[anahtar] = sadakat_map

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
        raw_by_key[anahtar] = row_map

        n_ic = h["n_ic"]
        n_dis = h["n_dis"]
        modeller.append(
            {
                "anahtar": anahtar,
                "llm": llm,
                "yapilandirma": h["yapilandirma"],
                "yapilandirma_adi": h["yapilandirma_adi"],
                "rerank": rerank,
                "ajan": ajan,
                "tag": full_tag,
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
                "yanlis_ret_katmanlari": yanlis_ret_katmanlari,
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
            -(m["baglam"] / m["n_ic"] if m["n_ic"] else 0.0),
            m["medyan_sure_sn"] if m["medyan_sure_sn"] is not None else 9999.0,
        )
    )

    by_llm: dict[str, list[dict]] = {}
    for m in modeller:
        by_llm.setdefault(m["llm"], []).append(m)
    config_order = {"tek_adim": 0, "reranker": 1, "ajan": 2, "reranker+ajan": 3}
    yapilandirma_karsilastirmasi = [
        {
            "llm": llm,
            "yapilandirmalar": sorted(items, key=lambda x: config_order.get(x["yapilandirma"], 9)),
        }
        for llm, items in by_llm.items()
        if len(items) > 1
    ]

    sorular: list[dict] = []
    for qid in question_order:
        meta = question_meta[qid]
        sonuclar: dict[str, dict] = {}
        for m in modeller:
            anahtar = m["anahtar"]
            r = raw_by_key.get(anahtar, {}).get(qid)
            if not r:
                continue
            skor = r.get("skor") or {}
            if r.get("hata"):
                sonuclar[anahtar] = {
                    "dogru": False,
                    "hata": True,
                    "sure_sn": r.get("sure_sn"),
                }
            elif meta["tur"] == "kapsam_disi":
                sonuclar[anahtar] = {
                    "dogru": bool(skor.get("dogru_ret")),
                    "dogru_ret": bool(skor.get("dogru_ret")),
                    "katman": skor.get("katman"),
                    "sure_sn": r.get("sure_sn"),
                }
            else:
                sonuclar[anahtar] = {
                    "dogru": bool(skor.get("dogru")),
                    "baglam": bool(skor.get("baglam")),
                    "atif": bool(skor.get("atif")),
                    "icerik": bool(skor.get("icerik")),
                    "yanlis_ret": bool(skor.get("yanlis_ret")),
                    "katman": skor.get("katman"),
                    "sure_sn": r.get("sure_sn"),
                    "tam_destekli": sadakat_by_key.get(anahtar, {}).get(qid),
                }
        sorular.append({**meta, "sonuclar": sonuclar})

    genis_arama = parse_genis_check()
    genis_evals = parse_genis_evals()
    genis_katman = (
        {"arama": genis_arama, "acik_eval": genis_evals}
        if (genis_arama or genis_evals)
        else None
    )

    return {
        "uretim_tarihi": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "modeller": modeller,
        "yapilandirma_karsilastirmasi": yapilandirma_karsilastirmasi,
        "rerank_karsilastirma": parse_rerank_compare(),
        "arama_deneyleri": parse_compare_retrieval(),
        "genis_katman": genis_katman,
        "gecmis": gecmis,
        "sorular": sorular,
    }


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pano = build_pano()
    OUT_PATH.write_text(json.dumps(pano, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(
        f"Yazıldı: {OUT_PATH} ({len(pano['modeller'])} yapılandırma, "
        f"{len(pano['gecmis'])} çalıştırma, {len(pano['sorular'])} soru)"
    )


if __name__ == "__main__":
    main()
