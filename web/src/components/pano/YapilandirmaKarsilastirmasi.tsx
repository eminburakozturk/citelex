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

  const anaGrup = gruplar[0];
  const tekAdim = anaGrup?.yapilandirmalar.find((y) => y.yapilandirma === "tek_adim");
  const ajan = anaGrup?.yapilandirmalar.find((y) => y.yapilandirma === "ajan");

  return (
    <section aria-labelledby="yapilandirma-baslik" className="min-w-0 space-y-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <span className="text-[11px] font-semibold tracking-wider text-subtle uppercase">Bölüm 1</span>
          <h2 id="yapilandirma-baslik" className="font-serif text-xl font-medium text-ink">
            Yapılandırma karşılaştırması — ajan neden fark yarattı?
          </h2>
        </div>
        <p className="text-xs text-muted">Tek adım, reranker ve ajan modu aynı soru setinde</p>
      </div>

      {gruplar.map((g) => (
        <div key={g.llm} className="space-y-4 rounded-xl border border-line bg-panel p-4 shadow-xs">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="text-xs font-medium text-muted">
              Model: <strong className="text-ink">{kisaModelAdi(g.llm)}</strong>
            </span>
            {tekAdim && ajan && (
              <span className="rounded-full bg-accent-soft px-2.5 py-0.5 text-[11px] font-semibold text-accent">
                +{Math.round(((ajan.dogru_orani ?? 0) - (tekAdim.dogru_orani ?? 0)) * 100)} puan (ajan)
              </span>
            )}
          </div>

          {g === anaGrup && tekAdim && ajan && (
            <p role="note" className="rounded-lg bg-panel-soft/80 px-3.5 py-2.5 text-xs leading-relaxed text-ink">
              Ajan modu, eşik altındaki soruları yeniden arayarak yanlış &ldquo;bilmiyorum&rdquo; sayısını{" "}
              <strong className="text-accent">{tekAdim.yanlis_ret}</strong>&apos;den{" "}
              <strong className="text-ok">{ajan.yanlis_ret}</strong>&apos;e düşürdü ({tekAdim.dogru}/{tekAdim.n_ic} →{" "}
              {ajan.dogru}/{ajan.n_ic}).
            </p>
          )}

          <div className="space-y-2.5">
            {[...g.yapilandirmalar].reverse().map((m) => {
              const pct = Math.round((m.dogru_orani ?? 0) * 100);
              const vurgulu = m.yapilandirma === "ajan" || m.yapilandirma === "reranker+ajan";
              return (
                <div
                  key={m.anahtar}
                  className={`space-y-1 rounded-lg px-3 py-2 ${
                    vurgulu ? "bg-accent-soft/50" : "bg-bg/60"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 text-xs tabular-nums">
                    <span className={`capitalize ${vurgulu ? "font-semibold text-accent" : "font-medium text-ink"}`}>
                      {m.yapilandirma_adi}
                    </span>
                    <span className="font-semibold text-ink">
                      {m.dogru}/{m.n_ic} <span className="font-normal text-muted">({yuzde(m.dogru_orani)})</span>
                    </span>
                  </div>
                  <div className="h-2.5 w-full overflow-hidden rounded-full bg-panel-soft">
                    <div
                      className={`h-full rounded-full ${vurgulu ? "bg-accent-btn" : "bg-info"}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="w-full overflow-x-auto border-t border-line pt-3">
            <table className="w-full border-collapse text-left text-xs sm:text-sm">
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
        </div>
      ))}

      {rerank && (
        <div className="w-full overflow-x-auto rounded-xl border border-line bg-panel shadow-xs">
          <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-line px-3.5 py-2.5 text-xs text-muted">
            <span>
              Reranker arama ölçümü (<code className="text-ink">{rerank.dosya}</code> · bge-reranker-v2-m3, ilk 30 aday)
            </span>
            {rerank.not && <span>{rerank.not}</span>}
          </div>
          <table className="w-full border-collapse text-left text-xs">
            <thead>
              <tr className="border-b border-line bg-bg/50 text-muted">
                <th className="px-3.5 py-2 font-medium">Kanal</th>
                <th className="px-3.5 py-2 font-medium">Yöntem</th>
                <th className="px-3.5 py-2 text-right font-medium">n</th>
                <th className="px-3.5 py-2 text-right font-medium">R@1</th>
                <th className="px-3.5 py-2 text-right font-medium">R@3</th>
                <th className="px-3.5 py-2 text-right font-medium">R@5</th>
                <th className="px-3.5 py-2 text-right font-medium">MRR</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line tabular-nums">
              {rerank.satirlar.map((s, i) => (
                <tr key={`${s.kanal}-${s.yontem}-${i}`} className="hover:bg-bg/60">
                  <td className="px-3.5 py-2 text-ink">{s.kanal}</td>
                  <td className="px-3.5 py-2 font-medium text-ink">{s.yontem}</td>
                  <td className="px-3.5 py-2 text-right text-muted">{s.n}</td>
                  <td className="px-3.5 py-2 text-right text-ink">{s.r1}</td>
                  <td className="px-3.5 py-2 text-right text-ink">{s.r3}</td>
                  <td className="px-3.5 py-2 text-right text-ink">{s.r5}</td>
                  <td className="px-3.5 py-2 text-right font-semibold text-ink">{s.mrr.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
