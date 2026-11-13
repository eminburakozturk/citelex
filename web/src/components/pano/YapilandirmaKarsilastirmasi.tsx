"use client";

import { KATMAN_ADI, RerankKarsilastirma, YapilandirmaGrubu, kisaModelAdi, yuzde } from "./types";

function katmanOzeti(katmanlar: Record<string, number>): string {
  const entries = Object.entries(katmanlar);
  if (entries.length === 0) return "—";
  return entries.map(([k, v]) => `${KATMAN_ADI[k] ?? k}: ${v}`).join(" · ");
}

export function YapilandirmaKarsilastirmasi({
  gruplar,
  rerank,
}: {
  gruplar: YapilandirmaGrubu[];
  rerank: RerankKarsilastirma | null;
}) {
  if (gruplar.length === 0 && !rerank) return null;

  return (
    <section aria-labelledby="yapilandirma-baslik" className="space-y-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 id="yapilandirma-baslik" className="text-base font-semibold">
          Yapılandırma karşılaştırması
        </h2>
        <p className="text-xs text-muted">Tek adım, reranker ve ajan modu aynı soru setinde</p>
      </div>

      {gruplar.map((g) => (
        <div key={g.llm} className="overflow-x-auto rounded-lg border border-line bg-panel">
          <div className="border-b border-line px-3 py-2 text-xs font-medium text-muted">
            Model: <span className="text-ink">{kisaModelAdi(g.llm)}</span>
          </div>
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr className="border-b border-line text-xs text-muted">
                <th className="px-3 py-2 font-medium">Yapılandırma</th>
                <th className="px-3 py-2 text-right font-medium">Doğru</th>
                <th className="px-3 py-2 text-right font-medium">Bağlam</th>
                <th className="px-3 py-2 text-right font-medium">Yanlış &ldquo;bilmiyorum&rdquo;</th>
                <th className="px-3 py-2 font-medium">Katman dağılımı</th>
                <th className="px-3 py-2 text-right font-medium">Kapsam dışı ret</th>
                <th className="px-3 py-2 text-right font-medium">Medyan süre</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line tabular-nums">
              {g.yapilandirmalar.map((m) => (
                <tr key={m.anahtar} className="hover:bg-bg/60">
                  <td className="px-3 py-2 font-medium text-ink capitalize">{m.yapilandirma_adi}</td>
                  <td className="px-3 py-2 text-right whitespace-nowrap">
                    <span className="font-semibold">{yuzde(m.dogru_orani)}</span>{" "}
                    <span className="text-xs text-muted">
                      ({m.dogru}/{m.n_ic})
                    </span>
                  </td>
                  <td className="px-3 py-2 text-right whitespace-nowrap">
                    {m.baglam}/{m.n_ic} ({yuzde(m.n_ic ? m.baglam / m.n_ic : null)})
                  </td>
                  <td className="px-3 py-2 text-right whitespace-nowrap">
                    {m.yanlis_ret}/{m.n_ic} ({yuzde(m.yanlis_ret_orani)})
                  </td>
                  <td className="px-3 py-2 text-xs text-muted">{katmanOzeti(m.yanlis_ret_katmanlari)}</td>
                  <td className="px-3 py-2 text-right whitespace-nowrap">
                    {m.dogru_ret}/{m.n_dis} ({yuzde(m.dogru_ret_orani)})
                  </td>
                  <td className="px-3 py-2 text-right whitespace-nowrap">
                    {m.medyan_sure_sn != null ? `${m.medyan_sure_sn.toFixed(2)} sn` : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}

      {rerank && (
        <div className="overflow-x-auto rounded-lg border border-line bg-panel">
          <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-line px-3 py-2 text-xs text-muted">
            <span>
              Reranker arama ölçümü (<code className="text-ink">{rerank.dosya}</code> · bge-reranker-v2-m3, ilk 30 aday)
            </span>
            {rerank.not && <span>{rerank.not}</span>}
          </div>
          <table className="w-full border-collapse text-left text-xs">
            <thead>
              <tr className="border-b border-line text-muted">
                <th className="px-3 py-2 font-medium">Kanal</th>
                <th className="px-3 py-2 font-medium">Yöntem</th>
                <th className="px-3 py-2 text-right font-medium">n</th>
                <th className="px-3 py-2 text-right font-medium">R@1</th>
                <th className="px-3 py-2 text-right font-medium">R@3</th>
                <th className="px-3 py-2 text-right font-medium">R@5</th>
                <th className="px-3 py-2 text-right font-medium">MRR</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line tabular-nums">
              {rerank.satirlar.map((s, i) => (
                <tr key={`${s.kanal}-${s.yontem}-${i}`} className="hover:bg-bg/60">
                  <td className="px-3 py-1.5 text-ink">{s.kanal}</td>
                  <td className="px-3 py-1.5 font-medium text-ink">{s.yontem}</td>
                  <td className="px-3 py-1.5 text-right text-muted">{s.n}</td>
                  <td className="px-3 py-1.5 text-right text-ink">{s.r1}</td>
                  <td className="px-3 py-1.5 text-right text-ink">{s.r3}</td>
                  <td className="px-3 py-1.5 text-right text-ink">{s.r5}</td>
                  <td className="px-3 py-1.5 text-right font-semibold text-ink">{s.mrr.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
