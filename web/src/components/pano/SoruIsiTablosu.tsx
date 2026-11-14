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

  const referansModel = modeller[0] ?? null;
  const referansEtiket = referansModel
    ? yapilandirmaEtiketi(referansModel.llm, referansModel.yapilandirma, referansModel.yapilandirma_adi)
    : "";

  const gosterilen = sorular.filter((q) => {
    if (filtre === "hepsi") return true;
    if (filtre === "basarisiz") {
      return modeller.some((m) => q.sonuclar[m.anahtar] && !q.sonuclar[m.anahtar].dogru);
    }
    if (filtre === "kanun") return q.tur === "kanun" || q.tur === "kanun+yonetmelik";
    if (filtre === "yonetmelik") return q.tur === "yonetmelik" || q.tur === "teblig" || q.tur === "kanun+yonetmelik";
    return q.tur === filtre;
  });

  const gosterilenIdler = new Set(gosterilen.map((g) => g.id));

  return (
    <section aria-labelledby="isi-tablo-baslik" className="min-w-0 space-y-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <span className="text-[11px] font-semibold tracking-wider text-subtle uppercase">Bölüm 7</span>
          <h2 id="isi-tablo-baslik" className="font-serif text-xl font-medium text-ink">
            Soru × Model başarı tablosu
          </h2>
        </div>
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
              className={`inline-flex min-h-[40px] items-center rounded-full border px-3.5 py-2 transition-colors ${
                acik
                  ? "border-accent-btn bg-accent-btn font-medium text-accent-ink"
                  : "border-line bg-panel text-muted hover:text-ink"
              }`}
            >
              {f.ad}
            </button>
          );
        })}
      </div>

      {referansModel && sorular.length > 0 && (
        <div className="space-y-2.5 rounded-xl border border-line bg-panel p-4 shadow-xs">
          <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
            <span className="font-medium text-ink">
              Özet harita ({referansEtiket} · {sorular.length} soru)
            </span>
            <div className="flex flex-wrap items-center gap-3 text-[11px] text-muted">
              <span className="inline-flex items-center gap-1">
                <span className="h-2 w-2 rounded-xs bg-ok" /> Doğru
              </span>
              <span className="inline-flex items-center gap-1">
                <span className="h-2 w-2 rounded-xs bg-amber-500" /> Yanlış ret / kısmi sadakat
              </span>
              <span className="inline-flex items-center gap-1">
                <span className="h-2 w-2 rounded-xs bg-accent" /> Başarısız
              </span>
            </div>
          </div>

          <div className="grid grid-cols-7 gap-1.5 sm:grid-cols-14">
            {sorular.map((q) => {
              const s = q.sonuclar[referansModel.anahtar];
              const goster = gosterilenIdler.has(q.id);
              const ok = s?.dogru;
              const renk = !s
                ? "bg-panel-soft text-muted"
                : ok
                  ? "bg-ok-bg text-ok"
                  : s.yanlis_ret
                    ? "bg-warn-bg text-warn-ink"
                    : "bg-accent-soft text-accent";
              return (
                <button
                  key={q.id}
                  type="button"
                  disabled={!s}
                  onClick={() => s && setSecili({ q, etiket: referansEtiket, s })}
                  title={s ? `${q.id}: ${q.soru} (${hucreBasligi(referansEtiket, q.tur, s)})` : q.id}
                  aria-label={`${q.id}: ${s ? (ok ? "doğru" : "başarısız") : "veri yok"}`}
                  className={`flex min-h-[40px] flex-col items-center justify-center rounded-lg border border-transparent text-[11px] font-semibold tabular-nums transition-opacity hover:border-accent ${renk} ${
                    goster ? "opacity-100" : "opacity-25"
                  }`}
                >
                  <span className="text-[10px] opacity-80">{q.id}</span>
                  <span>{!s ? "—" : ok ? "✓" : "✗"}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {secili && (
        <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-line bg-panel px-4 py-2.5 text-xs shadow-xs">
          <div className="min-w-0 break-words">
            <span className="font-semibold text-ink">{secili.q.id}</span> ·{" "}
            <span className="text-ink">{secili.q.soru}</span>{" "}
            <span className="text-muted">({hucreBasligi(secili.etiket, secili.q.tur, secili.s)})</span>
          </div>
          <button
            type="button"
            onClick={() => setSecili(null)}
            className="inline-flex min-h-[40px] min-w-[44px] items-center justify-center rounded-lg border border-line px-3 py-1.5 text-muted hover:border-accent hover:text-ink"
          >
            Kapat
          </button>
        </div>
      )}

      <div className="w-full overflow-x-auto rounded-xl border border-line bg-panel shadow-xs">
        <table className="w-full border-collapse text-left text-xs">
          <thead>
            <tr className="border-b border-line bg-bg/50 text-muted">
              <th className="px-2.5 py-2.5 font-medium">#</th>
              <th className="px-2.5 py-2.5 font-medium">Tür</th>
              <th className="min-w-[16rem] px-2.5 py-2.5 font-medium">Soru</th>
              {modeller.map((m) => {
                const etiket = yapilandirmaEtiketi(m.llm, m.yapilandirma, m.yapilandirma_adi);
                return (
                  <th key={m.anahtar} className="px-2.5 py-2.5 text-center font-medium whitespace-nowrap" title={m.anahtar}>
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
                    ? "bg-ok-bg text-ok"
                    : s.yanlis_ret
                      ? "bg-warn-bg text-warn-ink"
                      : "bg-accent-soft text-accent";
                  return (
                    <td key={m.anahtar} className="p-1 text-center">
                      <button
                        type="button"
                        onClick={() => setSecili({ q, etiket, s })}
                        title={hucreBasligi(etiket, q.tur, s)}
                        className={`relative inline-flex h-10 min-w-[40px] items-center justify-center rounded-lg font-semibold ${hucreSinif}`}
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
