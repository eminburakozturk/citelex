"use client";

import { GenisKatmanVerisi } from "./types";

export function GenisKatmanBolumu({ veri }: { veri?: GenisKatmanVerisi | null }) {
  if (!veri || (!veri.arama && veri.acik_eval.length === 0)) return null;

  const { arama, acik_eval } = veri;

  return (
    <section aria-labelledby="genis-katman-pano-baslik" className="min-w-0 space-y-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <span className="text-[11px] font-semibold tracking-wider text-subtle uppercase">Bölüm 5</span>
          <div className="flex flex-wrap items-center gap-2">
            <h2 id="genis-katman-pano-baslik" className="font-serif text-xl font-medium text-ink">
              Geniş katman (~900 kanun)
            </h2>
            <span
              role="note"
              className="rounded-full border border-warn-border bg-warn-bg px-2.5 py-0.5 text-[11px] font-semibold text-warn-ink"
            >
              TASLAK soru seti
            </span>
          </div>
        </div>
        <p className="text-xs text-muted">Derin katman eşiği geçemediğinde devreye giren yedek kanal</p>
      </div>

      <p role="note" className="rounded-xl border border-warn-border bg-warn-bg px-4 py-3 text-xs leading-relaxed text-warn-ink">
        Geniş katman soru seti (<code>eval/genis_sorular.jsonl</code>: 15 kapsam içi + 3 kapsam dışı) ve açık
        değerlendirme beklenen cevapları <strong>TASLAK</strong> olup hukuki doğrulama bekler; eşik ve yönlendirme bu sete
        göre ayarlanmamıştır. Bilinen tasarım sınırı: derin katman benzer bir soruyu yakalarsa geniş katmana hiç gidilmez
        (ör. <code>g13</code> devlet memuru analık izni → İş Kanunu m. 74 ile 0,717 eşleşmesi; 0,05 fark kuralı sonrası
        yönlendirildi).
      </p>

      {arama && (
        <div className="space-y-3 rounded-xl border border-line bg-panel p-4 shadow-xs">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h3 className="text-sm font-semibold text-ink">
              Arama ölçümü (<code>{arama.dosya}</code> · LLM yok)
            </h3>
            {arama.not && <span className="text-xs text-muted">{arama.not}</span>}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left text-xs sm:text-sm">
              <thead>
                <tr className="border-b border-line bg-bg/50 text-xs text-muted">
                  <th className="px-3.5 py-2 font-medium">Ölçüt</th>
                  <th className="px-3.5 py-2 text-right font-medium">Değer</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line tabular-nums">
                {arama.ozet.map((o) => (
                  <tr key={o.olcut} className="hover:bg-bg/60">
                    <td className="px-3.5 py-2 text-ink">{o.olcut}</td>
                    <td className="px-3.5 py-2 text-right font-semibold whitespace-nowrap text-ink">{o.deger}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {arama.sorular.length > 0 && (
            <details className="border-t border-line pt-2 text-xs">
              <summary className="flex min-h-[40px] cursor-pointer items-center text-muted hover:text-ink">
                Soru bazında geniş katman arama ayrıntısı ({arama.sorular.length} soru)
              </summary>
              <div className="mt-2 overflow-x-auto">
                <table className="w-full border-collapse text-left text-xs">
                  <thead>
                    <tr className="border-b border-line text-muted">
                      <th className="px-2 py-1.5 font-medium">#</th>
                      <th className="min-w-[14rem] px-2 py-1.5 font-medium">Soru</th>
                      <th className="px-2 py-1.5 font-medium whitespace-nowrap">Beklenen</th>
                      <th className="px-2 py-1.5 font-medium whitespace-nowrap">Kanal</th>
                      <th className="px-2 py-1.5 text-center font-medium whitespace-nowrap">Bağlam</th>
                      <th className="px-2 py-1.5 text-right font-medium whitespace-nowrap">Sıra</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-line tabular-nums">
                    {arama.sorular.map((q) => (
                      <tr key={q.id} className="hover:bg-bg/60">
                        <td className="px-2 py-1.5 font-mono text-muted">{q.id}</td>
                        <td className="px-2 py-1.5 text-ink">{q.soru}</td>
                        <td className="px-2 py-1.5 font-mono whitespace-nowrap text-muted">{q.beklenen}</td>
                        <td className="px-2 py-1.5 whitespace-nowrap text-muted">{q.kanal}</td>
                        <td className="px-2 py-1.5 text-center font-semibold text-ink">
                          {q.baglamda ? "✓" : "✗"}
                        </td>
                        <td className="px-2 py-1.5 text-right whitespace-nowrap text-muted">{q.sira}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </details>
          )}
        </div>
      )}

      {acik_eval.map((ev) => (
        <div key={ev.dosya} className="space-y-3 rounded-xl border border-line bg-panel p-4 shadow-xs">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h3 className="text-sm font-semibold text-ink">
              Açık değerlendirme — {ev.model ?? ev.dosya} (<code>{ev.dosya}</code>)
            </h3>
            {ev.bilgi && <span className="text-xs text-muted">{ev.bilgi}</span>}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left text-xs sm:text-sm">
              <thead>
                <tr className="border-b border-line bg-bg/50 text-xs text-muted">
                  <th className="px-3.5 py-2 font-medium">Ölçüt</th>
                  <th className="px-3.5 py-2 text-right font-medium">Tümü</th>
                  <th className="px-3.5 py-2 text-right font-medium">Mevzuat</th>
                  <th className="px-3.5 py-2 text-right font-medium">Karar</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line tabular-nums">
                {ev.olcutler.map((o) => (
                  <tr key={o.olcut} className="hover:bg-bg/60">
                    <td className="px-3.5 py-2 font-medium text-ink">{o.olcut}</td>
                    <td className="px-3.5 py-2 text-right whitespace-nowrap text-ink">{o.tumu}</td>
                    <td className="px-3.5 py-2 text-right whitespace-nowrap text-muted">{o.mevzuat}</td>
                    <td className="px-3.5 py-2 text-right whitespace-nowrap text-muted">{o.karar}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex flex-wrap justify-between gap-2 border-t border-line pt-2 text-xs text-muted">
            {ev.kapsam_disi && (
              <span>
                Kapsam dışı ret: <strong className="text-ink">{ev.kapsam_disi}</strong> (<code>d03</code> 7036 s.
                Kanun m. 3 cevabı nedeniyle)
              </span>
            )}
            {ev.diger && <span>{ev.diger}</span>}
          </div>
        </div>
      ))}
    </section>
  );
}
