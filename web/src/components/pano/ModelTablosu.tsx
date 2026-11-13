"use client";

import { ModelOzeti, kisaModelAdi, saglayiciAdi, tarihSaat, yuzde } from "./types";

export function ModelTablosu({ modeller }: { modeller: ModelOzeti[] }) {
  if (modeller.length === 0) {
    return <p className="text-sm text-muted">Tamamlanmış değerlendirme çalıştırması bulunamadı.</p>;
  }

  return (
    <section aria-labelledby="model-tablo-baslik" className="space-y-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 id="model-tablo-baslik" className="text-base font-semibold">
          Model karşılaştırması
        </h2>
        <p className="text-xs text-muted">Her modelin son tam çalıştırması</p>
      </div>

      <div className="overflow-x-auto rounded-lg border border-line bg-panel">
        <table className="w-full border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-line text-xs text-muted">
              <th className="px-3 py-2.5 font-medium">Model</th>
              <th className="px-3 py-2.5 text-right font-medium">Doğru oranı</th>
              <th className="px-3 py-2.5 text-right font-medium">Yanlış &ldquo;bilmiyorum&rdquo;</th>
              <th className="px-3 py-2.5 text-right font-medium">Kapsam dışı ret</th>
              <th className="px-3 py-2.5 text-right font-medium">Geçersiz atıf</th>
              <th className="px-3 py-2.5 text-right font-medium">Medyan süre</th>
              <th className="px-3 py-2.5 text-right font-medium">Sadakat</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line tabular-nums">
            {modeller.map((m) => (
              <tr key={m.llm} className="hover:bg-bg/60">
                <td className="px-3 py-2.5">
                  <div className="font-medium text-ink" title={m.llm}>
                    {kisaModelAdi(m.llm)}
                  </div>
                  <div className="text-xs text-muted">
                    {saglayiciAdi(m.llm)} · {tarihSaat(m.tarih)} · <code>{m.commit}</code>
                  </div>
                </td>
                <td className="px-3 py-2.5 text-right whitespace-nowrap">
                  <span className="font-semibold text-ink">{yuzde(m.dogru_orani)}</span>
                  <div className="text-xs text-muted">
                    {m.dogru}/{m.n_ic} · bağlam {m.baglam}/{m.n_ic}
                  </div>
                </td>
                <td className="px-3 py-2.5 text-right whitespace-nowrap">
                  <span>{yuzde(m.yanlis_ret_orani)}</span>
                  <div className="text-xs text-muted">
                    {m.yanlis_ret}/{m.n_ic}
                  </div>
                </td>
                <td className="px-3 py-2.5 text-right whitespace-nowrap">
                  <span>{yuzde(m.dogru_ret_orani)}</span>
                  <div className="text-xs text-muted">
                    {m.dogru_ret}/{m.n_dis}
                  </div>
                </td>
                <td className="px-3 py-2.5 text-right whitespace-nowrap">{m.gecersiz_atif}</td>
                <td className="px-3 py-2.5 text-right whitespace-nowrap">
                  {m.medyan_sure_sn != null ? `${m.medyan_sure_sn.toFixed(2)} sn` : "—"}
                </td>
                <td className="px-3 py-2.5 text-right whitespace-nowrap">
                  {m.sadakat ? (
                    <>
                      <span className="font-medium text-ink">{yuzde(m.sadakat.tam_destekli_orani)}</span>
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
