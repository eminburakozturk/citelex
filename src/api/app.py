"""Citelex HTTP API (FastAPI).

  POST /sor        {"soru": "...", "turler": ["kanun", "karar"] (isteğe bağlı tür filtresi)}  -> SSE akışı (varsayılan) veya ?akis=false ile tek JSON
       olaylar: baglam (numaralı kaynak listesi) -> parca* (cevap metni parçaları) -> sonuc (doğrulanmış cevap)
                hata (kullanıcıya gösterilebilir mesaj)
  GET  /kaynak?anahtar=is-kanunu:8 | kvkk-karar-2023-86   -> madde / karar metni (atıfa tıklanınca)
  GET  /saglik     -> Qdrant, koleksiyon, LLM adı, son güncelleme kontrolü

Güvenlik:
  - LLM anahtarı yalnız sunucu ortamında; hiçbir cevapta/logda yer almaz. Sağlayıcı hata gövdesi istemciye
    aktarılmaz (yalnız sunucu günlüğüne), istemci genel bir mesaj görür.
  - /sor istek sınırı: IP başına dakikalık ve günlük, ayrıca isteğe bağlı günlük toplam tavan (src/api/ratelimit.py).
  - Soru uzunluğu sınırlı (3-500 karakter). CORS yalnız CITELEX_CORS'ta sayılan kökenlere açık.

Ortam değişkenleri: CITELEX_LLM (gemini | ollama[:model]), CITELEX_EMBED_DEVICE (cpu | boş),
  CITELEX_RATE_DK (10), CITELEX_RATE_GUN (200), CITELEX_GUNLUK_TOPLAM (0 = kapalı),
  CITELEX_WEB_DIR (statik arayüz klasörü), CITELEX_SON_KONTROL (depo yoksa gösterilecek tarih),
  CITELEX_TRUST_PROXY (1: istemci IP'si X-Forwarded-For'un son değerinden), CITELEX_CORS (virgüllü köken listesi).

Çalıştırma: python -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000
"""
from __future__ import annotations

import json
import logging
import os
import re
import sqlite3
from collections.abc import Iterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.api.ratelimit import RateLimiter

log = logging.getLogger("citelex.api")
SOURCES_PATH = Path("configs/sources.json")
DB_PATH = Path("data/store/citelex.db")
FARK_DIR = Path(os.environ.get("CITELEX_FARK_DIR", "data/store/farklar"))
RE_FARK = re.compile(r"^[0-9T]{15}_[a-z]+_[A-Za-z0-9._-]+_\d+-\d+$")  # yol enjeksiyonuna karşı sıkı kalıp
RE_ANAHTAR = re.compile(r"^[a-z0-9-]{2,60}(:[0-9A-Za-zÇĞİÖŞÜçğıöşü /]{1,20})?$")
GIZLI_ALANLAR = ("ham", "esik", "kanal_top1", "dense_top1")  # istemciye gitmeyen iç alanlar

MSG_KOTA = "Dil modeli sağlayıcısının kotası doldu. Lütfen birkaç dakika sonra tekrar deneyin."
MSG_HATA = "Cevap üretilirken bir hata oluştu. Lütfen tekrar deneyin."
MSG_SINIR = {"dakika": "Çok sık soru gönderdiniz.", "gunluk": "Günlük soru sınırınıza ulaştınız.",
             "gunluk_toplam": "Sistemin günlük soru sınırı doldu."}


class Soru(BaseModel):
    soru: str = Field(min_length=3, max_length=500)
    turler: list[Literal["kanun", "yonetmelik", "teblig", "karar"]] | None = Field(default=None, min_length=1, max_length=4)


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


def make_answerer():
    from src.generate.answer import Answerer   # ağır içe aktarma (torch) yalnız gerçek çalıştırmada
    a = Answerer(os.environ.get("CITELEX_LLM", "gemini"), embed_device=os.environ.get("CITELEX_EMBED_DEVICE") or None)
    a.searcher.embedder.embed_query("ısınma")  # modeli açılışta yükle: ilk kullanıcı 30 sn beklemesin
    return a


def last_check() -> str | None:
    """Kaynakların en son hatasız kontrol edildiği an (güncelleme hattının runs tablosu)."""
    if not DB_PATH.exists():   # yayın ortamında depo yok: tarih yayın anında ortam değişkeniyle verilir
        return os.environ.get("CITELEX_SON_KONTROL") or None
    try:
        con = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
        try:
            row = con.execute("SELECT MAX(finished) FROM runs WHERE finished IS NOT NULL AND n_error = 0").fetchone()
        finally:
            con.close()
        return row[0] if row else None
    except sqlite3.Error:
        return None


def public(a: dict) -> dict:
    out = {k: v for k, v in a.items() if k not in GIZLI_ALANLAR}
    out["son_kontrol"] = last_check() or a.get("derlem_tarihi")
    return out


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def llm_error_message(e: Exception) -> str:
    return MSG_KOTA if getattr(e, "status", None) == 429 else MSG_HATA


def create_app(answerer=None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.answerer = answerer or make_answerer()
        yield

    app = FastAPI(title="Citelex API", version="0.1", lifespan=lifespan,
                  description="Kaynak gösteren mevzuat asistanı. Bu sistem hukuki tavsiye vermez.")
    app.state.limiter = RateLimiter(_env_int("CITELEX_RATE_DK", 10), _env_int("CITELEX_RATE_GUN", 200),
                                    _env_int("CITELEX_GUNLUK_TOPLAM", 0))
    origins = [o.strip() for o in os.environ.get("CITELEX_CORS", "http://localhost:3000").split(",") if o.strip()]
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
    sources = {v["belge_id"]: v for k, v in json.loads(SOURCES_PATH.read_text(encoding="utf-8")).items()
               if not k.startswith("_")} if SOURCES_PATH.exists() else {}

    def client_ip(request: Request) -> str:
        if os.environ.get("CITELEX_TRUST_PROXY") == "1":
            # Son değer bize bağlanan vekilin eklediğidir; baştaki değerleri istemci uydurabilir.
            xff = request.headers.get("x-forwarded-for", "")
            if xff:
                return xff.split(",")[-1].strip()
        return request.client.host if request.client else "?"

    @app.get("/saglik")
    def saglik(request: Request):
        ans = request.app.state.answerer
        try:
            n = ans.searcher.client.count(ans.searcher.name, exact=False).count
            qdrant = "ok"
        except Exception as e:  # noqa: BLE001
            log.warning("qdrant erişilemiyor: %s", e)
            n, qdrant = None, "erisilemiyor"
        body = {"durum": "ok" if qdrant == "ok" else "sorunlu", "qdrant": qdrant, "koleksiyon": ans.searcher.name,
                "parca_sayisi": n, "llm": ans.llm.name, "son_kontrol": last_check() or ans.cfg.get("derlem_tarihi")}
        return JSONResponse(body, status_code=200 if qdrant == "ok" else 503)

    @app.post("/sor")
    def sor(body: Soru, request: Request, akis: bool = Query(True)):
        ok, bekle, neden = request.app.state.limiter.check(client_ip(request))
        if not ok:
            raise HTTPException(429, detail=f"{MSG_SINIR[neden]} {bekle} saniye sonra tekrar deneyin.",
                                headers={"Retry-After": str(bekle)})
        ans = request.app.state.answerer
        soru = body.soru.strip()
        if not akis:
            try:
                return public(ans.answer(soru, body.turler))
            except Exception as e:  # noqa: BLE001
                log.exception("cevap hatası")
                raise HTTPException(503, detail=llm_error_message(e)) from None

        def gen() -> Iterator[str]:
            try:
                for olay, veri in ans.answer_stream(soru, body.turler):
                    yield sse(olay, public(veri) if olay == "sonuc" else veri)
            except Exception as e:  # noqa: BLE001 — akış başladıktan sonra HTTP kodu değiştirilemez: hata olayı
                log.exception("akış hatası")
                yield sse("hata", {"mesaj": llm_error_message(e)})

        return StreamingResponse(gen(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @app.get("/kaynak")
    def kaynak(request: Request, anahtar: str = Query(min_length=2, max_length=80)):
        """Atıf anahtarından kaynak metni: 'belge_id:madde_no' (mevzuat) veya 'kvkk-karar-YYYY-N'."""
        if not RE_ANAHTAR.match(anahtar):
            raise HTTPException(400, detail="Geçersiz kaynak anahtarı.")
        from qdrant_client import models
        s = request.app.state.answerer.searcher
        bid, _, mno = anahtar.partition(":")
        must = [models.FieldCondition(key="belge_id", match=models.MatchValue(value=bid))]
        if mno:
            must.append(models.FieldCondition(key="madde_no", match=models.MatchValue(value=mno)))
        pts, _ = s.client.scroll(s.name, scroll_filter=models.Filter(must=must), limit=100, with_payload=True)
        ps = [p.payload for p in pts]
        if not ps or (not mno and ps[0]["belge_tur"] != "karar"):
            raise HTTPException(404, detail="Kaynak bulunamadı.")
        ilk = ps[0]
        if ilk["belge_tur"] == "karar":
            sira = {"sikayet": 0, "savunma": 1, "degerlendirme": 2, "hukum": 3}
            ps.sort(key=lambda p: (sira.get(p.get("bolum"), 9), int(p["chunk_id"].rsplit("-", 1)[-1])))
            atif, url = f"KVKK Kurulu K. {ilk['belge_no']}", ilk.get("url")
        else:
            ps.sort(key=lambda p: (p.get("fikra_no") or 0, p.get("parca_no") or 0))
            for p in ps:   # bölünmüş uzun fıkra: giriş cümlesi yalnız ilk parçada gösterilir
                if (p.get("parca_no") or 1) > 1 and p.get("giris") and p["metin"].startswith(p["giris"]):
                    p["metin"] = p["metin"][len(p["giris"]):].lstrip("\n")
            atif = re.sub(r"/\d+$", "", ilk["atif"]) if ilk.get("fikra_no") is not None else ilk["atif"]
            url = sources.get(bid, {}).get("sayfa_url")
        return {"anahtar": anahtar, "atif": atif, "belge_tur": ilk["belge_tur"], "belge_adi": ilk["belge_adi"],
                "baslik": ilk.get("baslik"), "url": url, "karar_tarihi": ilk.get("karar_tarihi"),
                "mulga": all(p.get("mulga") for p in ps), "son_kontrol": last_check(),
                "parcalar": [{"fikra_no": p.get("fikra_no"), "bolum": p.get("bolum") if ilk["belge_tur"] == "karar" else None,
                              "metin": p["metin"], "mulga": bool(p.get("mulga"))} for p in ps],
                "dipnotlar": ilk.get("dipnotlar") or []}

    @app.get("/degisiklikler")
    def degisiklikler(limit: int = Query(20, ge=1, le=100)):
        """Son sürüm değişiklikleri (özet; madde/bölüm listesi, metin yok). Güncelleme hattının yazdığı farklar."""
        from src.update.diff import list_diffs
        return {"degisiklikler": list_diffs(FARK_DIR, limit), "son_kontrol": last_check()}

    @app.get("/degisiklik/{fark_id}")
    def degisiklik(fark_id: str):
        """Tek değişiklik: her değişen madde/bölüm için eski metin, yeni metin ve kelime farkı."""
        if not RE_FARK.match(fark_id):
            raise HTTPException(400, detail="Geçersiz değişiklik kimliği.")
        p = FARK_DIR / f"{fark_id}.json"
        if not p.is_file():
            raise HTTPException(404, detail="Değişiklik bulunamadı.")
        return json.loads(p.read_text(encoding="utf-8"))

    # Statik arayüz (web/out) aynı adresten sunulur: yayında tek adres, CORS gerekmez. API yolları önce eşleşir.
    web_dir = Path(os.environ.get("CITELEX_WEB_DIR", "web/out"))
    if web_dir.is_dir():
        app.mount("/", StaticFiles(directory=web_dir, html=True), name="web")
    return app


app = create_app()
