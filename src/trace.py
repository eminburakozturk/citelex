"""İzlenebilirlik: her sorunun araması, bağlamı, gecikmesi, modeli, token ve maliyeti.

İki çıkış (biri diğerine bağlı değil):
  1) logs/izler.jsonl (CITELEX_IZ_DOSYA): her soru için TEK satır özet; her zaman açık, bağımlılık yok.
     CITELEX_IZ_DOSYA=0 ile kapatılır. Soru metni de yazılır (hata ayıklama için) — halka açık yayında bu
     dosya sunucuda kalır, istemciye dönmez.
  2) OpenTelemetry span'leri (sor -> arama, llm): yalnız OTEL_EXPORTER_OTLP_ENDPOINT tanımlıysa ve
     opentelemetry paketleri kuruluysa. Yerelde Jaeger paneli: docker compose --profile izleme up -d,
     http://127.0.0.1:16686. Öznitelik adları OTel GenAI anlamsal kurallarına uyar (gen_ai.*).
Span'ler elle başlatılıp bitirilir (current context kullanılmaz): akışlı cevap üreteci StreamingResponse'ta
farklı iş parçacıklarında ilerler; bağlam ekle/çıkar iş parçacığı değişince bozulur.
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("citelex.trace")
_lock = threading.Lock()
_tracer = None
_tracer_ready = False


def _get_tracer():
    global _tracer, _tracer_ready
    if _tracer_ready:
        return _tracer
    _tracer_ready = True
    if not os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return None
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        log.warning("OTEL_EXPORTER_OTLP_ENDPOINT tanımlı ama opentelemetry paketleri yok; span gönderilmez")
        return None
    provider = TracerProvider(resource=Resource.create({"service.name": os.environ.get("OTEL_SERVICE_NAME", "citelex-api")}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))  # adres ortam değişkeninden
    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer("citelex")
    return _tracer


def _clean(attrs: dict) -> dict:
    out = {}
    for k, v in attrs.items():
        if v is None:
            continue
        if isinstance(v, (list, tuple)):
            v = [str(x) for x in v]
        elif not isinstance(v, (str, bool, int, float)):
            v = str(v)
        out[k] = v
    return out


class Span:
    """OTel span'i varsa onu sarar; yoksa yalnız süre ve öznitelik toplar."""

    def __init__(self, name: str, parent: "Span | None" = None, **attrs):
        self.name, self.attrs, self.t0 = name, dict(attrs), time.time()
        self._otel = None
        tr = _get_tracer()
        if tr is not None:
            from opentelemetry import trace
            ctx = trace.set_span_in_context(parent._otel) if parent is not None and parent._otel is not None else None
            self._otel = tr.start_span(name, context=ctx, attributes=_clean(attrs))

    def set(self, **attrs) -> None:
        self.attrs.update(attrs)
        if self._otel is not None:
            self._otel.set_attributes(_clean(attrs))

    def error(self, e: BaseException) -> None:
        self.set(hata=f"{type(e).__name__}: {str(e)[:200]}")
        if self._otel is not None:
            from opentelemetry.trace import Status, StatusCode
            self._otel.record_exception(e)
            self._otel.set_status(Status(StatusCode.ERROR))

    def end(self) -> float:
        sn = round(time.time() - self.t0, 3)
        if self._otel is not None:
            self._otel.end()
        return sn

    @property
    def trace_id(self) -> str | None:
        if self._otel is None:
            return None
        return format(self._otel.get_span_context().trace_id, "032x")


def usage_attrs(llm) -> dict:
    """LLM nesnesinin son çağrısından model/token/maliyet (yalnız OpenRouter bildiriyor; diğerlerinde boş)."""
    u = getattr(llm, "last_usage", None) or {}
    return {"gen_ai.request.model": getattr(llm, "last_model", None) or getattr(llm, "name", None),
            "gen_ai.usage.input_tokens": u.get("prompt_tokens"), "gen_ai.usage.output_tokens": u.get("completion_tokens"),
            "citelex.maliyet_usd": u.get("cost")}


def write_record(rec: dict) -> None:
    path = os.environ.get("CITELEX_IZ_DOSYA", "logs/izler.jsonl")
    if path == "0":
        return
    rec = {"zaman": datetime.now(timezone.utc).isoformat(timespec="seconds"), **rec}
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with _lock, p.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError as e:  # iz yazılamaması cevabı bozmamalı
        log.warning("iz yazılamadı: %s", e)
