"use client";

import { useState } from "react";
import { ModelOzeti, SoruSatiri, SoruSonucu, kisaModelAdi } from "./types";

type Filtre = "hepsi" | "basarisiz" | "kanun" | "yonetmelik" | "karar" | "kapsam_disi";

const TUR_ETIKET: Record<string, string> = {
  kanun: "Kanun",
  "kanun+yonetmelik": "Kanun+Yön.",
  yonetmelik: "Yönetmelik",
  teblig: "Tebliğ",
  karar: "Kurul kararı",
  kapsam_disi: "Kapsam dışı",
};

const FILTRELER: { id: Filtre; ad: string }[] = [
  { id: "hepsi", ad: "Tümü" },
  { id: "basarisiz", ad: "En az bir ✗" },
  { id: "kanun", ad: "Kanun" },
  { id: "yonetmelik", ad: "Yönetmelik / Tebliğ" },
  { id: "karar", ad: "Kurul kararı" },
  { id: "kapsam_disi", ad: "Kapsam dışı" },
];

function hucreBasligi(llm: string, tur: string, s: SoruSonucu): string {
  const parcalar = [kisaModelAdi(llm)];
  if (s.hata) {
    parcalar.push("hata");
  } else if (tur === "kapsam_disi") {
    parcalar.push(s.dogru ? "doğru ret" : "uydurma cevap");
    if (s.katman) parcalar.push(`katman: ${s.katman}`);
  } else {
    parcalar.push(s.dogru ? "doğru" : "başarısız");
    parcalar.push(`bağlam:${s.baglam ? "✓" : "✗"} atıf:${s.atif ? "✓" : "✗"} içerik:${s.icerik ? "✓" : "✗"}`);
    if (s.yanlis_ret) parcalar.push(`yanlış bilmiyorum (${s.katman ?? "?"})`);
    if (s.sadik != null) parcalar.push(`hakem:${s.sadik ? "sadık" : "desteksiz"}`);
  }
  if (s.sure_sn != null) parcalar.push(`${s.sure_sn} sn`);
  return parcalar.join(" · ");
}

export function SoruIsiTablosu({ modeller, sorular }: { modeller: ModelOzeti[]; sorular: SoruSatiri[] }) {
  const [filtre, setFiltre] = useState<Filtre>("hepsi");
  const [secili, setSecili] = useState<{ q: SoruSatiri; llm: string; s: SoruSonucu } | null>(null);

  const gosterilen = sorular.filter((q) => {
    if (filtre === "hepsi") return true;
    if (filtre === "basarisiz") {
      return modeller.some((m) => q.sonuclar[m.llm] && !q.sonuclar[m.llm].dogru);
    }
    if (filtre === "kanun") return q.tur === "kanun" || q.tur === "kanun+yonetmelik";
    if (filtre === "yonetmelik") return q.tur === "yonetmelik" || q.tur === "teblig" || q.tur === "kanun+yonetmelik";
    return q.tur === filtre;
  });

  return (
    <section aria-labelledby="isi-tablo-baslik" className="space-y-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 id="isi-tablo-baslik" className="text-base font-semibold">
          Soru × Model başarı tablosu
        </h2>
        <p className="text-xs text-muted">
          {gosterilen.length}/{sorular.length} soru · ayrıntı için hücreye tıklayın
        </p>
      </div>

      <div className="flex flex-wrap gap-1.5 text-xs">
        {FILTRELER.map((f) => {
          const acik = filtre === f.id;
          return (
            <button
              key={f.id}
              type="button"
              aria-pressed={acik}
              onClick={() => setFiltre(f.id)}
              className={`rounded-full border px-2.5 py-1 ${
                acik ? "border-accent bg-accent-soft text-ink" : "border-line bg-panel text-muted hover:text-ink"
              }`}
            >
              {f.ad}
            </button>
          );
        })}
      </div>

      {secili && (
        <div className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-line bg-panel px-3 py-2 text-xs">
          <div>
            <span className="font-semibold text-ink">{secili.q.id}</span> ·{" "}
            <span className="text-ink">{kisaModelAdi(secili.llm)}</span>:{" "}
            <span className="text-muted">{hucreBasligi(secili.llm, secili.q.tur, secili.s)}</span>
          </div>
          <button
            type="button"
            onClick={() => setSecili(null)}
            className="rounded border border-line px-2 py-0.5 text-muted hover:text-ink"
          >
            Kapat
          </button>
        </div>
      )}

      <div className="overflow-x-auto rounded-lg border border-line bg-panel">
        <table className="w-full border-collapse text-left text-xs">
          <thead>
            <tr className="border-b border-line text-muted">
              <th className="px-2.5 py-2 font-medium">#</th>
              <th className="px-2.5 py-2 font-medium">Tür</th>
              <th className="min-w-[16rem] px-2.5 py-2 font-medium">Soru</th>
              {modeller.map((m) => (
                <th key={m.llm} className="px-2.5 py-2 text-center font-medium whitespace-nowrap" title={m.llm}>
                  {kisaModelAdi(m.llm)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {gosterilen.map((q) => (
              <tr key={q.id} className="hover:bg-bg/60">
                <td className="px-2.5 py-1.5 font-mono text-muted">{q.id}</td>
                <td className="px-2.5 py-1.5 whitespace-nowrap text-muted">{TUR_ETIKET[q.tur] ?? q.tur}</td>
                <td className="px-2.5 py-1.5 text-ink">{q.soru}</td>
                {modeller.map((m) => {
                  const s = q.sonuclar[m.llm];
                  if (!s) {
                    return (
                      <td key={m.llm} className="px-2 py-1.5 text-center text-muted">
                        —
                      </td>
                    );
                  }
                  const ok = s.dogru;
                  const hucreSinif = ok
                    ? "bg-emerald-500/12 text-emerald-700 dark:text-emerald-300"
                    : s.yanlis_ret
                      ? "bg-warn-bg text-warn-ink"
                      : "bg-accent-soft text-accent";
                  return (
                    <td key={m.llm} className="p-1 text-center">
                      <button
                        type="button"
                        onClick={() => setSecili({ q, llm: m.llm, s })}
                        title={hucreBasligi(m.llm, q.tur, s)}
                        className={`inline-flex h-6 w-8 items-center justify-center rounded font-semibold ${hucreSinif}`}
                      >
                        {ok ? "✓" : "✗"}
                      </button>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
