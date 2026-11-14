"use client";

import { KATMAN_ADI, ModelOzeti, yapilandirmaEtiketi } from "./types";

const KATMANLAR = ["arama_esigi", "llm", "atif_dogrulama"] as const;

export function EsikEtkisiKutusu({ modeller }: { modeller: ModelOzeti[] }) {
  if (modeller.length === 0) return null;

  return (
    <section aria-labelledby="esik-etkisi-baslik" className="min-w-0 space-y-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <span className="text-[11px] font-semibold tracking-wider text-subtle uppercase">Bölüm 3</span>
          <h2 id="esik-etkisi-baslik" className="font-serif text-xl font-medium text-ink">
            Eşik etkisi — yanlış &ldquo;bilmiyorum&rdquo; katmanları
          </h2>
        </div>
        <p className="text-xs text-muted">Kapsam içi sorularda gereksiz reddin hangi aşamada oluştuğu</p>
      </div>

      <div className="rounded-xl border border-line bg-panel p-4 shadow-xs">
        <div className="mb-3 flex flex-wrap gap-4 text-xs text-muted">
          <span className="inline-flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-sm bg-accent-btn" />
            {KATMAN_ADI.arama_esigi}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-sm bg-amber-500" />
            {KATMAN_ADI.llm}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-sm bg-info" />
            {KATMAN_ADI.atif_dogrulama}
          </span>
        </div>

        <div className="space-y-2.5">
          {modeller.map((m) => {
            const k = m.yanlis_ret_katmanlari ?? {};
            const esik = k.arama_esigi ?? 0;
            const llm = k.llm ?? 0;
            const atif = k.atif_dogrulama ?? 0;
            const toplam = m.yanlis_ret;
            const payda = Math.max(m.n_ic, 1);
            return (
              <div key={m.anahtar} className="grid items-center gap-2 sm:grid-cols-[15rem_1fr_auto]">
                <div className="text-xs font-medium text-ink">
                  {yapilandirmaEtiketi(m.llm, m.yapilandirma, m.yapilandirma_adi)}
                </div>
                <div className="flex h-3 overflow-hidden rounded-full bg-panel-soft" title={`${toplam}/${m.n_ic} yanlış bilmiyorum`}>
                  {esik > 0 && (
                    <div
                      className="bg-accent-btn"
                      style={{ width: `${(esik / payda) * 100}%` }}
                      title={`${KATMAN_ADI.arama_esigi}: ${esik}`}
                    />
                  )}
                  {llm > 0 && (
                    <div
                      className="bg-amber-500"
                      style={{ width: `${(llm / payda) * 100}%` }}
                      title={`${KATMAN_ADI.llm}: ${llm}`}
                    />
                  )}
                  {atif > 0 && (
                    <div
                      className="bg-info"
                      style={{ width: `${(atif / payda) * 100}%` }}
                      title={`${KATMAN_ADI.atif_dogrulama}: ${atif}`}
                    />
                  )}
                </div>
                <div className="break-words text-left text-xs text-muted tabular-nums sm:whitespace-nowrap sm:text-right">
                  <strong className="text-ink">{toplam}</strong>/{m.n_ic} (
                  {KATMANLAR.filter((ad) => (k[ad] ?? 0) > 0)
                    .map((ad) => `${KATMAN_ADI[ad]}: ${k[ad]}`)
                    .join(", ") || "yok"}
                  )
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
