"use client";

import { useState } from "react";
import { ModelOzeti, SoruSatiri, SoruSonucu, yapilandirmaEtiketi } from "./types";

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

function hucreBasligi(etiket: string, tur: string, s: SoruSonucu): string {
  const parcalar = [etiket];
  if (s.hata) {
    parcalar.push("hata");
  } else if (tur === "kapsam_disi") {
    parcalar.push(s.dogru ? "doğru ret" : "uydurma cevap");
    if (s.katman) parcalar.push(`katman: ${s.katman}`);
  } else {
    parcalar.push(s.dogru ? "doğru" : "başarısız");
    parcalar.push(`bağlam:${s.baglam ? "✓" : "✗"} atıf:${s.atif ? "✓" : "✗"} içerik:${s.icerik ? "✓" : "✗"}`);
    if (s.yanlis_ret) parcalar.push(`yanlış bilmiyorum (${s.katman ?? "?"})`);
    if (s.tam_destekli != null) {
      parcalar.push(`sadakat:${s.tam_destekli ? "tam destekli" : "kısmen/desteksiz"}`);
    }
  }
  if (s.sure_sn != null) parcalar.push(`${s.sure_sn} sn`);
  return parcalar.join(" · ");
}

export function SoruIsiTablosu({ modeller, sorular }: { modeller: ModelOzeti[]; sorular: SoruSatiri[] }) {
  const [filtre, setFiltre] = useState<Filtre>("hepsi");
  const [secili, setSecili] = useState<{ q: SoruSatiri; etiket: string; s: SoruSonucu } | null>(null);

  const gosterilen = sorular.filter((q) => {
    if (filtre === "hepsi") return true;
    if (filtre === "basarisiz") {
      return modeller.some((m) => q.sonuclar[m.anahtar] && !q.sonuclar[m.anahtar].dogru);
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

      <div className="flex flex-wrap gap-2 text-xs">
        {FILTRELER.map((f) => {
          const acik = filtre === f.id;
          return (
            <button
              key={f.id}
              type="button"
              aria-pressed={acik}
              onClick={() => setFiltre(f.id)}
              className={`inline-flex min-h-[40px] items-center rounded-full border px-3.5 py-2 ${
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
          <div className="min-w-0 break-words">
            <span className="font-semibold text-ink">{secili.q.id}</span> ·{" "}
            <span className="text-ink">{secili.etiket}</span>:{" "}
            <span className="text-muted">{hucreBasligi(secili.etiket, secili.q.tur, secili.s)}</span>
          </div>
          <button
            type="button"
            onClick={() => setSecili(null)}
            className="inline-flex min-h-[40px] min-w-[44px] items-center justify-center rounded border border-line px-3 py-1.5 text-muted hover:text-ink"
          >
            Kapat
          </button>
        </div>
      )}

      <div className="w-full overflow-x-auto rounded-lg border border-line bg-panel">
        <table className="w-full border-collapse text-left text-xs">
          <thead>
            <tr className="border-b border-line text-muted">
              <th className="px-2.5 py-2 font-medium">#</th>
              <th className="px-2.5 py-2 font-medium">Tür</th>
              <th className="min-w-[16rem] px-2.5 py-2 font-medium">Soru</th>
              {modeller.map((m) => {
                const etiket = yapilandirmaEtiketi(m.llm, m.yapilandirma, m.yapilandirma_adi);
                return (
                  <th key={m.anahtar} className="px-2.5 py-2 text-center font-medium whitespace-nowrap" title={m.anahtar}>
                    {etiket}
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {gosterilen.map((q) => (
              <tr key={q.id} className="hover:bg-bg/60">
                <td className="px-2.5 py-1.5 font-mono text-muted">{q.id}</td>
                <td className="px-2.5 py-1.5 whitespace-nowrap text-muted">{TUR_ETIKET[q.tur] ?? q.tur}</td>
                <td className="px-2.5 py-1.5 text-ink">{q.soru}</td>
                {modeller.map((m) => {
                  const s = q.sonuclar[m.anahtar];
                  const etiket = yapilandirmaEtiketi(m.llm, m.yapilandirma, m.yapilandirma_adi);
                  if (!s) {
                    return (
                      <td key={m.anahtar} className="px-2 py-1.5 text-center text-muted">
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
                    <td key={m.anahtar} className="p-1 text-center">
                      <button
                        type="button"
                        onClick={() => setSecili({ q, etiket, s })}
                        title={hucreBasligi(etiket, q.tur, s)}
                        className={`relative inline-flex h-10 min-w-[40px] items-center justify-center rounded font-semibold ${hucreSinif}`}
                      >
                        {ok ? "✓" : "✗"}
                        {s.tam_destekli === false && (
                          <span
                            aria-label="Kısmen veya desteksiz iddia"
                            className="absolute right-1 top-1 h-1.5 w-1.5 rounded-full bg-amber-500"
                          />
                        )}
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
