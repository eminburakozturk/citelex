"use client";

import { useState } from "react";
import {
  BirimDurumu,
  DegisiklikAyrintisi,
  belgeBasligi,
  birimEtiketi,
  turAdi,
  zamanMetni,
} from "./types";

type Gorunum = "satir_ici" | "yan_yana";

const DURUM_ETIKET: Record<BirimDurumu, { ad: string; sinif: string }> = {
  degisti: { ad: "Değişti", sinif: "bg-warn-bg text-warn-ink" },
  eklendi: { ad: "Eklendi", sinif: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300" },
  silindi: { ad: "Silindi", sinif: "bg-accent-soft text-accent" },
};

export function DegisiklikAyrinti({ veri }: { veri: DegisiklikAyrintisi }) {
  const [gorunum, setGorunum] = useState<Gorunum>("satir_ici");

  return (
    <section aria-label="Değişiklik ayrıntısı" className="space-y-4 rounded-lg border border-line bg-panel p-4">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-line pb-3">
        <div className="min-w-0 space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="break-words text-base font-semibold text-ink">{belgeBasligi(veri.doc_key, veri.belge_id)}</h2>
            <span className="rounded bg-bg px-2 py-0.5 text-xs text-muted">{turAdi(veri.tur)}</span>
          </div>
          <p className="break-words text-xs text-muted">
            Değişiklik zamanı: {zamanMetni(veri.zaman)} · Sürüm #{veri.eski.surum_id} (<code>{veri.eski.hash}</code>) →
            Sürüm #{veri.yeni.surum_id} (<code>{veri.yeni.hash}</code>)
          </p>
          {veri.url && (
            <p className="text-xs">
              <a
                href={veri.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex min-h-[40px] items-center text-accent underline"
              >
                Resmî kaynakta aç
              </a>
            </p>
          )}
        </div>

        <div className="inline-flex flex-wrap rounded-md border border-line bg-bg p-0.5 text-xs" role="group" aria-label="Fark görünümü">
          <button
            type="button"
            aria-pressed={gorunum === "satir_ici"}
            onClick={() => setGorunum("satir_ici")}
            className={`min-h-[40px] rounded px-3 py-2 ${
              gorunum === "satir_ici" ? "bg-panel font-medium text-ink shadow-xs" : "text-muted hover:text-ink"
            }`}
          >
            Satır içi fark
          </button>
          <button
            type="button"
            aria-pressed={gorunum === "yan_yana"}
            onClick={() => setGorunum("yan_yana")}
            className={`min-h-[40px] rounded px-3 py-2 ${
              gorunum === "yan_yana" ? "bg-panel font-medium text-ink shadow-xs" : "text-muted hover:text-ink"
            }`}
          >
            Eski / Yeni metin
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {veri.birimler.map((b) => {
          const d = DURUM_ETIKET[b.durum] ?? { ad: b.durum, sinif: "bg-bg text-muted" };
          return (
            <article key={b.birim} className="space-y-2 rounded-md border border-line bg-bg/50 p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h3 className="text-sm font-semibold text-ink">{birimEtiketi(b.etiket)}</h3>
                <span className={`rounded px-2 py-0.5 text-xs font-medium ${d.sinif}`}>{d.ad}</span>
              </div>

              {gorunum === "satir_ici" ? (
                <div className="kanun-metni whitespace-pre-wrap break-words rounded border border-line bg-panel p-3 text-[15px] text-ink">
                  {b.fark.map(([islem, metin], i) => {
                    if (islem === "=") return <span key={i}>{metin}</span>;
                    if (islem === "-") {
                      return (
                        <del
                          key={i}
                          className="rounded bg-red-500/15 px-0.5 text-red-700 line-through decoration-red-500/80 dark:text-red-300"
                        >
                          {metin}
                        </del>
                      );
                    }
                    return (
                      <ins
                        key={i}
                        className="rounded bg-emerald-500/15 px-0.5 font-medium text-emerald-800 no-underline dark:text-emerald-300"
                      >
                        {metin}
                      </ins>
                    );
                  })}
                </div>
              ) : (
                <div className="grid gap-3 md:grid-cols-2">
                  <div className="min-w-0 space-y-1 rounded border border-line bg-panel p-3">
                    <div className="text-xs font-medium text-muted">
                      Eski metin · Sürüm #{veri.eski.surum_id} ({zamanMetni(veri.eski.ilk_gorulme)})
                    </div>
                    <p className="kanun-metni whitespace-pre-wrap break-words text-[15px] text-ink">
                      {b.eski ?? "— (bu sürümde yok)"}
                    </p>
                  </div>
                  <div className="min-w-0 space-y-1 rounded border border-line bg-panel p-3">
                    <div className="text-xs font-medium text-muted">
                      Yeni metin · Sürüm #{veri.yeni.surum_id} ({zamanMetni(veri.yeni.ilk_gorulme)})
                    </div>
                    <p className="kanun-metni whitespace-pre-wrap break-words text-[15px] text-ink">
                      {b.yeni ?? "— (bu sürümde kaldırıldı)"}
                    </p>
                  </div>
                </div>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}
