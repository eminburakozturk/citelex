"use client";

import { ModelOzeti, kisaModelAdi, saglayiciAdi, tarihSaat, yuzde } from "./types";

export function ModelTablosu({ modeller }: { modeller: ModelOzeti[] }) {
  if (modeller.length === 0) {
    return <p className="text-sm text-muted">Tamamlanmış değerlendirme çalıştırması bulunamadı.</p>;
  }

  const tekAdimSadakat = modeller.filter((m) => m.yapilandirma === "tek_adim" && m.sadakat != null);

  return (
    <section aria-labelledby="model-tablo-baslik" className="min-w-0 space-y-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <span className="text-[11px] font-semibold tracking-wider text-subtle uppercase">Bölüm 2</span>
          <h2 id="model-tablo-baslik" className="font-serif text-xl font-medium text-ink">
            Model karşılaştırması — kelime eşleşmesi yetmez
          </h2>
        </div>
        <p className="text-xs text-muted">Her model ve yapılandırmanın son tam çalıştırması</p>
      </div>

      {tekAdimSadakat.length >= 2 && (
        <div className="space-y-3 rounded-xl border border-line bg-panel p-4 shadow-xs">
          <p role="note" className="rounded-lg bg-warn-bg px-3.5 py-2.5 text-xs leading-relaxed text-warn-ink">
            Anahtar kelime doğruluğu tek adım modellerde birbirine yakındı; her cümlenin kaynağa bağlı olup
            olmadığını ölçen <strong>LLM hakemli sadakat</strong> modelleri birbirinden ayırdı.
          </p>

          <div className="grid gap-3 md:grid-cols-3">
            {tekAdimSadakat.map((m) => {
              const dogruYuzde = Math.round((m.dogru_orani ?? 0) * 100);
              const sadakatYuzde = Math.round((m.sadakat?.tam_destekli_orani ?? 0) * 100);
              return (
                <div key={m.anahtar} className="space-y-2 rounded-lg border border-line bg-bg/60 p-3">
                  <div className="flex items-baseline justify-between gap-2">
                    <span className="truncate text-xs font-semibold text-ink">{kisaModelAdi(m.llm)}</span>
                    <span className="shrink-0 text-[11px] tabular-nums text-subtle">
                      {m.sadakat!.tam_destekli}/{m.sadakat!.cevap} tam destekli
                    </span>
                  </div>
                  <div className="space-y-1.5 text-[11px] tabular-nums">
                    <div className="flex items-center gap-2">
                      <span className="w-12 text-muted">Doğru</span>
                      <div className="h-2 flex-1 overflow-hidden rounded-full bg-panel-soft">
                        <div className="h-full rounded-full bg-info" style={{ width: `${dogruYuzde}%` }} />
                      </div>
                      <span className="w-9 text-right font-medium text-ink">%{dogruYuzde}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-12 text-muted">Sadakat</span>
                      <div className="h-2 flex-1 overflow-hidden rounded-full bg-panel-soft">
                        <div className="h-full rounded-full bg-accent-btn" style={{ width: `${sadakatYuzde}%` }} />
                      </div>
                      <span className="w-9 text-right font-semibold text-accent">%{sadakatYuzde}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="w-full overflow-x-auto rounded-xl border border-line bg-panel shadow-xs">
        <table className="w-full border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-line bg-bg/50 text-xs text-muted">
              <th className="px-3.5 py-2.5 font-medium">Model / yapılandırma</th>
              <th className="px-3.5 py-2.5 text-right font-medium">Doğru oranı</th>
              <th className="px-3.5 py-2.5 text-right font-medium">Yanlış &ldquo;bilmiyorum&rdquo;</th>
              <th className="px-3.5 py-2.5 text-right font-medium">Kapsam dışı ret</th>
              <th className="px-3.5 py-2.5 text-right font-medium">Geçersiz atıf</th>
              <th className="px-3.5 py-2.5 text-right font-medium">Medyan süre</th>
              <th className="px-3.5 py-2.5 text-right font-medium">Sadakat</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line tabular-nums">
            {modeller.map((m) => (
              <tr key={m.anahtar} className="hover:bg-bg/60">
                <td className="px-3.5 py-2.5">
                  <div className="flex flex-wrap items-center gap-1.5 font-medium text-ink" title={m.llm}>
                    <span>{kisaModelAdi(m.llm)}</span>
                    {m.yapilandirma !== "tek_adim" && (
                      <span className="rounded-full bg-accent-soft px-2 py-0.5 text-[11px] font-medium text-accent">
                        + {m.yapilandirma_adi}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-muted">
                    {saglayiciAdi(m.llm)} · {tarihSaat(m.tarih)} · <code>{m.commit}</code>
                  </div>
                </td>
                <td className="px-3.5 py-2.5 text-right whitespace-nowrap">
                  <span className="font-semibold text-ink">{yuzde(m.dogru_orani)}</span>
                  <div className="text-xs text-muted">
                    {m.dogru}/{m.n_ic} · bağlam {m.baglam}/{m.n_ic}
                  </div>
                </td>
                <td className="px-3.5 py-2.5 text-right whitespace-nowrap">
                  <span>{yuzde(m.yanlis_ret_orani)}</span>
                  <div className="text-xs text-muted">
                    {m.yanlis_ret}/{m.n_ic}
                  </div>
                </td>
                <td className="px-3.5 py-2.5 text-right whitespace-nowrap">
                  <span>{yuzde(m.dogru_ret_orani)}</span>
                  <div className="text-xs text-muted">
                    {m.dogru_ret}/{m.n_dis}
                  </div>
                </td>
                <td className="px-3.5 py-2.5 text-right whitespace-nowrap">{m.gecersiz_atif}</td>
                <td className="px-3.5 py-2.5 text-right whitespace-nowrap">
                  {m.medyan_sure_sn != null ? `${m.medyan_sure_sn.toFixed(2).replace(".", ",")} sn` : "—"}
                </td>
                <td className="px-3.5 py-2.5 text-right whitespace-nowrap">
                  {m.sadakat ? (
                    <>
                      <span className="font-semibold text-ink">{yuzde(m.sadakat.tam_destekli_orani)}</span>
                      <div className="text-xs text-muted">
                        {m.sadakat.tam_destekli}/{m.sadakat.cevap} tam destekli · iddia {yuzde(m.sadakat.destekli_orani)}
                      </div>
                    </>
                  ) : (
                    <span className="text-muted">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
