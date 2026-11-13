"""LLM hakemli sadakat ölçütü: cevaptaki her iddia, atıf yaptığı kaynak metniyle destekleniyor mu?

Neden: run_eval'deki `icerik` anahtar kelime eşleşmesidir; doğru kelimeyi yanlış bağlamda yazan cevabı doğru
sayabiliyor (e37). Hakem cevabı iddialara (cümlelere) ayırır ve her birini atıf yaptığı kaynağın metnine göre
etiketler: destekli / kismen / desteksiz. Atıfsız cümle, cevabın atıf yaptığı kaynakların herhangi birine göre
değerlendirilir.

Girdi: run_eval ham çıktısı (results/eval_<tag>.jsonl). [n] -> baglam_anahtar[n-1] (LLM'e verilen bağlamın sırası).
Kaynak metni: eval/fixtures (madde: maddenin TAMAMI — bağlama bazen yalnız ilgili fıkralar girer, yani hakem
modelin gördüğünden biraz FAZLASINI görür, ölçüt bu yönde hafif cömerttir; karar: hüküm + Kurul değerlendirmesi).

Ölçütler (yalnız cevap verilen kapsam içi sorular):
  sadik      : hiç "desteksiz" iddia yok (cevap düzeyi)
  iddia oranı: destekli iddia / tüm iddia
Hakem skoru eşik/prompt ayarında KULLANILMAZ (KARARLAR.md 2026-11-13); hakemin kendisi elle örneklemle kontrol edilir.
Önyargı: hakem, değerlendirdiği cevabı üreten modelle aynı olmamalı (kendi cevabını kayırma eğilimi).

Kullanım: python -m eval.judge results/eval_openrouter_deepseek_deepseek_v4.1_flash_1017.jsonl \
              --hakem openrouter:nvidia/nemotron-3-ultra-550b-a55b:free
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

from src import config  # noqa: F401  (.env yükler)
from src.generate.llm import make_llm
from eval.gate import FIX, load_gz

MAX_KAYNAK = 15000  # 6000 iken karar metni kesiliyor, hakem kesilen kısımdaki ifadeye "desteksiz" diyordu (qwen e41)
ETIKETLER = ("destekli", "kismen", "desteksiz", "uyari")
HAKEM_SURUM = "v2"  # v1: uyarı etiketi ve paraphrase/atlama kuralı yoktu (elle kontrolde aşırı katı bulundu)

SYSTEM = """Sen bir hukuk metni denetçisisin. Görevin bir cevabın KAYNAKLARINA SADIK olup olmadığını denetlemek:
cevapta kaynakta olmayan, kaynakla çelişen ya da yanlış kaynağa dayandırılmış bilgi var mı?
Yalnız verilen kaynak metinlerine bak; hukuki doğruluğu kendi bilginle değil kaynakla ölç.

Cevabı tek tek iddialara (genellikle cümlelere) ayır. Her iddia için:
- atif: iddianın sonundaki [n] numaraları (yoksa boş liste)
- etiket:
  "destekli"  : iddia, atıf yaptığı kaynak(lar)da yazıyor ya da doğrudan çıkıyor. Farklı kelimelerle
                özetlemek (paraphrase) ve kaynaktaki bazı ayrıntıları ATLAMAK sadakatsizlik değildir.
                Kaynak bir başka maddeye numarayla atıf yapıyorsa (ör. "5 inci maddede öngörülen ilke") ve
                cevap o maddeyi adıyla anıyorsa, soru ve diğer kaynaklarla tutarlı olduğu sürece destekli say.
  "kismen"    : iddianın bir parçası (ör. bir sayı, süre, koşul, istisna) kaynakta YOK ya da kaynaktan FARKLI
  "desteksiz" : kaynakta yok, kaynakla çelişiyor ya da yanlış kaynağa atıf yapılmış
  "uyari"     : kaynağın içeriği hakkında bilgi vermeyen yöntem/uyarı cümlesi (ör. "bu karar somut olaya
                özgüdür", "genel kural olarak sunulamaz", "hukuki tavsiye değildir"). Bunlar sayılmaz.
  Atıfsız iddiayı verilen kaynakların herhangi birine göre değerlendir.
- gerekce: tek kısa cümle; "kismen" ve "desteksiz" için kaynakta neyin olmadığını/farklı olduğunu söyle

YALNIZ şu JSON'u döndür, başka metin yazma:
{"iddialar": [{"iddia": "...", "atif": [1], "etiket": "destekli", "gerekce": "..."}]}"""


def kaynak_metinleri() -> dict[str, str]:
    out: dict[str, str] = {}
    for a in load_gz(FIX / "articles.jsonl.gz"):
        key = f"{a['belge_id']}:{a['madde_no']}"
        if a.get("mulga") or key in out:
            continue
        metin = "\n".join(f"({f['fikra_no']}) {f['metin']}" if f.get("fikra_no") else f["metin"] for f in a["fikralar"])
        out[key] = f"{a.get('atif', key)} — {a.get('baslik') or ''}\n{metin}"
    kararlar: dict[str, list[dict]] = {}
    for c in load_gz(FIX / "chunks_karar.jsonl.gz"):
        kararlar.setdefault(c["belge_id"], []).append(c)
    for bid, cs in kararlar.items():
        cs.sort(key=lambda c: c["chunk_id"])
        sec = [c for c in cs if c["bolum"] == "hukum"] + [c for c in cs if c["bolum"] == "degerlendirme"]
        out[bid] = f"{cs[0]['atif']}\n" + "\n".join(c["metin"] for c in (sec or cs))
    return out


def parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("JSON yok")
    j = json.loads(m.group(0))
    for i in j["iddialar"]:
        if i.get("etiket") not in ETIKETLER:
            raise ValueError(f"geçersiz etiket: {i.get('etiket')}")
    return j


def judge_one(llm, row: dict, metinler: dict[str, str]) -> dict:
    nolar = sorted({int(n) for n in re.findall(r"\[(\d+)\]", row["cevap"])})
    bag = row.get("baglam_anahtar") or []
    parcalar = []
    for n in nolar:
        if 1 <= n <= len(bag):
            metin = metinler.get(bag[n - 1], "(kaynak metni bulunamadı)")[:MAX_KAYNAK]
            parcalar.append(f"[{n}] {metin}")
    user = f"SORU: {row['soru']}\n\nKAYNAKLAR:\n" + "\n\n".join(parcalar) + f"\n\nCEVAP:\n{row['cevap']}"
    son_hata = None
    for _ in range(2):
        try:
            j = parse_json(llm.generate(SYSTEM, user, max_tokens=2500))
            break
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            son_hata = e
    else:
        return {"hata": f"hakem çıktısı ayrıştırılamadı: {son_hata}"}
    ids = [i for i in j["iddialar"] if i["etiket"] != "uyari"]
    say = {e: sum(i["etiket"] == e for i in ids) for e in ETIKETLER}
    u = getattr(llm, "last_usage", None) or {}
    u = {k: u.get(k) for k in ("prompt_tokens", "completion_tokens", "cost")}
    return {"iddialar": j["iddialar"], "hakem_surum": HAKEM_SURUM, **say, "uyari": len(j["iddialar"]) - len(ids), "n_iddia": len(ids), "sadik": say["desteksiz"] == 0 and len(ids) > 0,
            "hakem_model": getattr(llm, "last_model", None) or llm.name, "kullanim": u}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("girdi")
    ap.add_argument("--hakem", default=None, help="ör. openrouter:<model> (cevabı üreten modelden farklı olmalı)")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--sadece-rapor", action="store_true", help="girdi bir sadakat_*.jsonl; hakem çağrılmaz")
    args = ap.parse_args()
    if args.sadece_rapor:
        rapor_yeniden(args.girdi)
        return

    rows = [json.loads(l) for l in open(args.girdi, encoding="utf-8")]
    rows = [r for r in rows if not r.get("hata") and r.get("tur") != "kapsam_disi"
            and not r["skor"].get("yanlis_ret")][: args.limit]
    llm = make_llm(args.hakem)
    metinler = kaynak_metinleri()
    tag = Path(args.girdi).stem.removeprefix("eval_")
    hakem_tag = re.sub(r"[^a-z0-9.]+", "_", args.hakem.lower())
    out = Path(f"results/sadakat_{tag}__hakem_{hakem_tag}.jsonl")
    sonuc = []
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        for i, r in enumerate(rows, 1):
            t = time.time()
            try:
                h = judge_one(llm, r, metinler)
            except Exception as e:  # noqa: BLE001 — tek sorunun hatası durdurmasın; metriğe girmez
                h = {"hata": f"{type(e).__name__}: {str(e)[:200]}"}
            h["sure_sn"] = round(time.time() - t, 1)
            kayit = {"id": r["id"], "soru": r["soru"], "cevap": r["cevap"], "icerik": r["skor"]["icerik"],
                     "dogru": r["skor"]["dogru"], **h}
            sonuc.append(kayit)
            fh.write(json.dumps(kayit, ensure_ascii=False) + "\n")
            print(f"[{i}/{len(rows)}] {r['id']} " + (h.get("hata") or
                  f"sadik={h['sadik']} d/k/x={h['destekli']}/{h['kismen']}/{h['desteksiz']}"), flush=True)

    rapor(sonuc, out, tag, args.hakem)


def rapor(sonuc: list[dict], out: Path, tag: str, hakem: str) -> None:
    """Asıl ölçüt TAM DESTEKLİ cevap (ne kısmen ne desteksiz iddia): hakem aynı sorunu bir koşuda 'desteksiz',
    diğerinde 'kismen' etiketleyebiliyor (ölçüldü: nemotron e17, e26); ikisinin toplamı daha kararlı."""
    ok = [s for s in sonuc if not s.get("hata")]
    for s in ok:
        s["tam_destekli"] = s["kismen"] == 0 and s["desteksiz"] == 0 and s["n_iddia"] > 0
    n_idd = sum(s["n_iddia"] for s in ok)
    dest = sum(s["destekli"] for s in ok)
    tam = sum(s["tam_destekli"] for s in ok)
    sadik = sum(s["sadik"] for s in ok)
    ayrisan = [s for s in ok if s["dogru"] != s["tam_destekli"]]
    pct = lambda a, b: f"{a}/{b} (%{100 * a / max(b, 1):.0f})"  # noqa: E731
    L = [f"# Sadakat (LLM hakem) — {tag}", "",
         f"Hakem: {hakem} (talimat {HAKEM_SURUM}) | cevap: {len(ok)} (hata {len(sonuc) - len(ok)}) | iddia: {n_idd} | "
         f"hakem maliyeti: ${sum((s.get('kullanim') or {}).get('cost') or 0 for s in ok):.4f}", "",
         "Yalnız cevap verilen kapsam içi sorular. Hakem kaynak metnine göre etiketler; kendi hukuk bilgisini kullanmaz "
         "(talimat). Hakem de hata yapabilir: elle kontrol örneklemi KARARLAR.md'de. Kısmen/desteksiz sınırı koşudan "
         "koşuya oynayabildiği için asıl ölçüt 'tam destekli'dir.", "",
         "| Ölçüt | Değer |", "|---|---|",
         f"| **Tam destekli cevap** (kısmen/desteksiz iddia yok) | {pct(tam, len(ok))} |",
         f"| Desteksiz iddiası olmayan cevap | {pct(sadik, len(ok))} |",
         f"| Destekli iddia | {pct(dest, n_idd)} |",
         f"| Kısmen | {sum(s['kismen'] for s in ok)} |", f"| Desteksiz | {sum(s['desteksiz'] for s in ok)} |",
         f"| Uyarı cümlesi (sayılmadı) | {sum(s['uyari'] for s in ok)} |", "",
         "## Anahtar kelime ölçütüyle (`dogru`) ayrışanlar", "",
         "| # | dogru (anahtar) | tam destekli (hakem) | Kısmen/desteksiz iddialar |", "|---|---|---|---|"]
    for s in ayrisan:
        kotu = "; ".join(f"[{i['etiket']}] {i['iddia'][:90]} — {i.get('gerekce', '')[:90]}"
                         for i in s["iddialar"] if i["etiket"] in ("kismen", "desteksiz")) or "—"
        L.append(f"| {s['id']} | {'✓' if s['dogru'] else '✗'} | {'✓' if s['tam_destekli'] else '✗'} | {kotu.replace('|', '/')} |")
    out.with_suffix(".md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(L[:14]))


def rapor_yeniden(jsonl: str) -> None:
    """Hakemi yeniden çağırmadan, kayıtlı sonuçtan raporu üret."""
    p = Path(jsonl)
    sonuc = [json.loads(l) for l in open(p, encoding="utf-8")]
    tag, _, hk = p.stem.removeprefix("sadakat_").partition("__hakem_")
    rapor(sonuc, p, tag, hk)


if __name__ == "__main__":
    main()
