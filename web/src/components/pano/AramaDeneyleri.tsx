"use client";

import { AramaDeneyleriVerisi } from "./types";

export function AramaDeneyleri({ veri }: { veri?: AramaDeneyleriVerisi | null }) {
  if (!veri) return null;

  return (
    <section aria-labelledby="arama-deneyleri-baslik" className="min-w-0 space-y-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <span className="text-[11px] font-semibold tracking-wider text-subtle uppercase">Bölüm 4</span>
          <h2 id="arama-deneyleri-baslik" className="font-serif text-xl font-medium text-ink">
            Arama deneyleri
          </h2>
        </div>
        <p className="text-xs text-muted">
          <code>{veri.dosya}</code> · Reranker kapalı
        </p>
      </div>

      <p role="note" className="rounded-xl border border-warn-border bg-warn-bg px-3.5 py-2.5 text-xs leading-relaxed text-warn-ink">
        Bu sette tek başına dense, hibrit RRF&apos;den biraz iyi (2 soru farkı, gürültü sınırında); soru seti derlem
        metninden üretildiği için dense&apos;i kayırabilir.
      </p>

      {veri.parcalama_yontem.length > 0 && (
        <div className="w-full overflow-x-auto rounded-xl border border-line bg-panel shadow-xs">
          <div className="border-b border-line px-3.5 py-2.5 text-xs font-medium text-muted">
            1. Parçalama × yöntem (Qdrant, iki kanal)
          </div>
          <table className="w-full border-collapse text-left text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-line bg-bg/50 text-xs text-muted">
                <th className="px-3.5 py-2 font-medium">Parçalama</th>
                <th className="px-3.5 py-2 font-medium">Yöntem</th>
                <th className="px-3.5 py-2 text-right font-medium whitespace-nowrap">Mevzuat R@1</th>
                <th className="px-3.5 py-2 text-right font-medium whitespace-nowrap">Mevzuat R@5</th>
                <th className="px-3.5 py-2 text-right font-medium whitespace-nowrap">Mevzuat MRR</th>
                <th className="px-3.5 py-2 text-right font-medium whitespace-nowrap">Karar R@1</th>
                <th className="px-3.5 py-2 text-right font-medium whitespace-nowrap">Karar R@3</th>
                <th className="px-3.5 py-2 text-right font-medium whitespace-nowrap">Süre (sn/soru)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line tabular-nums">
              {veri.parcalama_yontem.map((s, i) => (
                <tr key={`${s.parcalama}-${s.yontem}-${i}`} className="hover:bg-bg/60">
                  <td className="px-3.5 py-2 text-ink">{s.parcalama}</td>
                  <td className="px-3.5 py-2 font-medium text-ink">{s.yontem}</td>
                  <td className="px-3.5 py-2 text-right whitespace-nowrap text-ink">{s.mevzuat_r1}</td>
                  <td className="px-3.5 py-2 text-right whitespace-nowrap text-ink">{s.mevzuat_r5}</td>
                  <td className="px-3.5 py-2 text-right font-semibold whitespace-nowrap text-ink">
                    {s.mevzuat_mrr.toFixed(3).replace(".", ",")}
                  </td>
                  <td className="px-3.5 py-2 text-right whitespace-nowrap text-ink">{s.karar_r1}</td>
                  <td className="px-3.5 py-2 text-right whitespace-nowrap text-ink">{s.karar_r3}</td>
                  <td className="px-3.5 py-2 text-right whitespace-nowrap text-muted">
                    {s.sure_sn.toFixed(2).replace(".", ",")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {veri.sozcuksel.length > 0 && (
        <div className="w-full overflow-x-auto rounded-xl border border-line bg-panel shadow-xs">
          <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-line px-3.5 py-2.5 text-xs text-muted">
            <span className="font-medium">2. Sözcüksel kanal: BM25 ve bge-m3 sparse (hibrit parçalar, mevzuat)</span>
            {veri.sozcuksel_not && <span>{veri.sozcuksel_not}</span>}
          </div>
          <table className="w-full border-collapse text-left text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-line bg-bg/50 text-xs text-muted">
                <th className="px-3.5 py-2 font-medium">Yöntem</th>
                <th className="px-3.5 py-2 text-right font-medium">R@1</th>
                <th className="px-3.5 py-2 text-right font-medium">R@5</th>
                <th className="px-3.5 py-2 text-right font-medium">MRR@5</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line tabular-nums">
              {veri.sozcuksel.map((s, i) => (
                <tr key={`${s.yontem}-${i}`} className="hover:bg-bg/60">
                  <td className="px-3.5 py-2 font-medium text-ink">{s.yontem}</td>
                  <td className="px-3.5 py-2 text-right whitespace-nowrap text-ink">{s.r1}</td>
                  <td className="px-3.5 py-2 text-right whitespace-nowrap text-ink">{s.r5}</td>
                  <td className="px-3.5 py-2 text-right font-semibold whitespace-nowrap text-ink">
                    {s.mrr5.toFixed(3).replace(".", ",")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
