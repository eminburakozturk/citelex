"use client";

import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";
import { SiteKabugu } from "@/components/SiteKabugu";
import { GELISTIRICI_VERISI } from "@/content/gelistirici";

export default function GelistiriciSayfasi() {
  const [acikKarar, setAcikKarar] = useState<number | null>(0);
  const { kimlik, odaklar, kararlar, kronoloji, teknolojiler } = GELISTIRICI_VERISI;

  return (
    <SiteKabugu aktif="gelistirici" baslikAlt="Geliştirici ve mimari kararlar">
      <div className="space-y-6">
        <section
          aria-label="Geliştirici profili"
          className="relative overflow-hidden rounded-xl border border-line bg-panel p-5 shadow-xs"
        >
          <div className="flex flex-wrap items-start gap-4">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full border border-line bg-panel-soft font-serif text-lg font-semibold text-accent">
              {kimlik.basHarfler}
            </div>
            <div className="min-w-0 flex-1 space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="font-serif text-2xl font-medium text-ink">{kimlik.adSoyad}</h1>
                <span className="rounded-full bg-accent-soft px-2.5 py-0.5 text-[11px] font-medium text-accent">
                  Citelex
                </span>
              </div>
              <p className="text-sm font-medium text-muted">{kimlik.unvan}</p>
              <p className="text-xs text-subtle">{kimlik.altBaslik}</p>
            </div>
          </div>

          <p className="mt-4 font-serif text-[15px] leading-relaxed text-ink">{kimlik.biyografi}</p>

          <p role="note" className="mt-3 rounded-lg bg-warn-bg px-3 py-2 text-xs text-warn-ink">
            Kararlar, tarihler ve teknoloji listesi gerçek proje kayıtlarından (KARARLAR.md) alınmıştır.
          </p>

          <div className="mt-4 grid grid-cols-3 gap-2 border-t border-line pt-4">
            {kimlik.baglantilar.map((b) => (
              <a
                key={b.etiket}
                href={b.href}
                aria-disabled={b.yerTutucu ? "true" : undefined}
                target={b.href.startsWith("http") ? "_blank" : undefined}
                rel={b.href.startsWith("http") ? "noopener noreferrer" : undefined}
                onClick={b.yerTutucu ? (e) => e.preventDefault() : undefined}
                title={b.yerTutucu ? "gelistirici.ts içinden bağlantı ekleyin" : b.etiket}
                className={`inline-flex min-h-[44px] items-center justify-center rounded-lg border px-3 py-2 text-xs font-medium transition-colors ${
                  b.yerTutucu
                    ? "border-dashed border-line bg-bg/60 text-muted"
                    : "border-line bg-panel-soft text-ink hover:border-accent hover:text-accent"
                }`}
              >
                {b.etiket}
              </a>
            ))}
          </div>
        </section>

        <section aria-labelledby="odak-baslik" className="space-y-3">
          <div className="flex items-baseline justify-between gap-2 px-1">
            <h2 id="odak-baslik" className="font-serif text-xl font-medium text-ink">
              Bu projede ne yaptım?
            </h2>
            <span className="text-xs text-subtle">3 temel odak</span>
          </div>

          <div className="grid gap-3 md:grid-cols-3">
            {odaklar.map((o) => (
              <article key={o.baslik} className="rounded-xl border border-line bg-panel p-4 shadow-xs">
                <div className="mb-2 flex items-center justify-between gap-2">
                  <h3 className="text-sm font-semibold text-ink">{o.baslik}</h3>
                  <span className="rounded-full bg-panel-soft px-2 py-0.5 text-[10px] font-semibold text-muted uppercase">
                    {o.etiket}
                  </span>
                </div>
                <p className="text-xs leading-relaxed text-muted">{o.aciklama}</p>
              </article>
            ))}
          </div>
        </section>

        <section aria-labelledby="kararlar-baslik" className="space-y-3">
          <div className="flex items-baseline justify-between gap-2 px-1">
            <h2 id="kararlar-baslik" className="font-serif text-xl font-medium text-ink">
              Verdiğim kararlar
            </h2>
            <span className="text-xs text-subtle">KARARLAR.md kayıtlarından 5 seçim</span>
          </div>

          <div className="space-y-2.5">
            {kararlar.map((k, idx) => {
              const acik = acikKarar === idx;
              return (
                <div key={k.baslik} className="overflow-hidden rounded-xl border border-line bg-panel shadow-xs">
                  <button
                    type="button"
                    aria-expanded={acik}
                    onClick={() => setAcikKarar(acik ? null : idx)}
                    className="flex min-h-[52px] w-full items-center justify-between gap-3 px-4 py-3 text-left transition-colors hover:bg-panel-soft/50"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <span className="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent-soft text-xs font-semibold tabular-nums text-accent">
                        {idx + 1}
                      </span>
                      <span className="text-sm font-medium text-ink">{k.baslik}</span>
                    </div>
                    <span className="shrink-0 text-xs text-muted">{acik ? "Gizle" : "Aç"}</span>
                  </button>

                  <AnimatePresence initial={false}>
                    {acik && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.18 }}
                        className="overflow-hidden border-t border-line bg-bg/50 px-4 py-3"
                      >
                        <div className="mb-1 text-[11px] font-medium text-accent">{k.tarih}</div>
                        <p className="text-xs leading-relaxed text-muted">{k.gerekce}</p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>
        </section>

        <section aria-labelledby="kronoloji-baslik" className="space-y-3">
          <div className="flex items-baseline justify-between gap-2 px-1">
            <h2 id="kronoloji-baslik" className="font-serif text-xl font-medium text-ink">
              Geliştirme kronolojisi
            </h2>
            <span className="text-xs text-subtle">git log · 11–14 Kasım 2026</span>
          </div>

          <div className="rounded-xl border border-line bg-panel p-5 shadow-xs">
            <ol className="relative space-y-5 border-l-2 border-line pl-5">
              {kronoloji.map((adim) => (
                <li key={adim.tarih} className="relative space-y-1">
                  <span
                    aria-hidden="true"
                    className="absolute -left-[25px] top-1.5 h-2.5 w-2.5 rounded-full border-2 border-panel bg-accent"
                  />
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <h3 className="text-sm font-semibold text-ink">{adim.baslik}</h3>
                    <span className="text-xs font-medium text-accent">{adim.tarih}</span>
                  </div>
                  <p className="text-xs leading-relaxed text-muted">{adim.detay}</p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section aria-labelledby="yigin-baslik" className="space-y-3">
          <div className="flex items-baseline justify-between gap-2 px-1">
            <h2 id="yigin-baslik" className="font-serif text-xl font-medium text-ink">
              Teknoloji yığını
            </h2>
            <span className="text-xs text-subtle">{teknolojiler.length} bileşen</span>
          </div>

          <div className="rounded-xl border border-line bg-panel p-4 shadow-xs">
            <div className="flex flex-wrap gap-2">
              {teknolojiler.map((t) => (
                <span
                  key={t}
                  className="rounded-lg border border-line bg-panel-soft px-3 py-1 text-xs font-medium text-ink"
                >
                  {t}
                </span>
              ))}
            </div>
          </div>
        </section>
      </div>
    </SiteKabugu>
  );
}
