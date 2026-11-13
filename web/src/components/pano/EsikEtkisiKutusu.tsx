"use client";

import { KATMAN_ADI, ModelOzeti, yapilandirmaEtiketi } from "./types";

const KATMANLAR = ["arama_esigi", "llm", "atif_dogrulama"] as const;

export function EsikEtkisiKutusu({ modeller }: { modeller: ModelOzeti[] }) {
  if (modeller.length === 0) return null;

  return (
    <section aria-labelledby="esik-etkisi-baslik" className="space-y-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 id="esik-etkisi-baslik" className="text-base font-semibold">
          Eşik etkisi — yanlış &ldquo;bilmiyorum&rdquo; katmanları
        </h2>
        <p className="text-xs text-muted">Kapsam içi sorularda gereksiz reddin hangi aşamada oluştuğu</p>
      </div>

      <div className="rounded-lg border border-line bg-panel p-4">
        <div className="mb-3 flex flex-wrap gap-4 text-xs text-muted">
          <span className="inline-flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-sm bg-accent" />
            {KATMAN_ADI.arama_esigi}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-sm bg-amber-500" />
            {KATMAN_ADI.llm}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-sm bg-sky-600" />
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
                <div className="flex h-3 overflow-hidden rounded-full bg-bg" title={`${toplam}/${m.n_ic} yanlış bilmiyorum`}>
                  {esik > 0 && (
                    <div
                      className="bg-accent"
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
                      className="bg-sky-600"
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
