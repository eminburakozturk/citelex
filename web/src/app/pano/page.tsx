"use client";

import { useEffect, useState } from "react";
import { SiteKabugu } from "@/components/SiteKabugu";
import { AramaDeneyleri } from "@/components/pano/AramaDeneyleri";
import { EsikEtkisiKutusu } from "@/components/pano/EsikEtkisiKutusu";
import { GenisKatmanBolumu } from "@/components/pano/GenisKatmanBolumu";
import { ModelTablosu } from "@/components/pano/ModelTablosu";
import { SoruIsiTablosu } from "@/components/pano/SoruIsiTablosu";
import { YapilandirmaKarsilastirmasi } from "@/components/pano/YapilandirmaKarsilastirmasi";
import { ZamanGrafigi } from "@/components/pano/ZamanGrafigi";
import { PanoVerisi, kisaModelAdi, tarihSaat, yuzde } from "@/components/pano/types";

export default function PanoSayfasi() {
  const [veri, setVeri] = useState<PanoVerisi | null>(null);
  const [hata, setHata] = useState<string | null>(null);

  useEffect(() => {
    fetch("/pano.json")
      .then((res) => {
        if (!res.ok) throw new Error("pano.json yüklenemedi.");
        return res.json() as Promise<PanoVerisi>;
      })
      .then((d) => setVeri(d))
      .catch((e) => setHata((e as Error).message));
  }, []);

  const modeller = veri?.modeller ?? [];
  const enIyiDogru = modeller[0] ?? null;
  const maxGecersiz =
    modeller.length > 0 ? Math.max(...modeller.map((m) => m.gecersiz_atif)) : null;
  // Üst kartlar TEK yapılandırmayı anlatır (en doğru olan); sadakat da onun sadakati — başka yapılandırmadan seçilmez.
  const enIyiSadakat = enIyiDogru?.sadakat?.tam_destekli_orani != null ? enIyiDogru : null;

  return (
    <SiteKabugu aktif="pano" genislik="genis" baslikAlt="Değerlendirme panosu">
      <div className="min-w-0 space-y-8">
        <section className="space-y-2">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="text-[11px] font-semibold tracking-wider text-accent uppercase">
              Ampirik Doğrulama
            </span>
            {veri && (
              <span className="rounded-full bg-panel-soft px-3 py-1 text-xs text-muted">
                Üretim: {tarihSaat(veri.uretim_tarihi)}
              </span>
            )}
          </div>
          <h1 className="font-serif text-3xl font-medium tracking-tight text-ink">
            Değerlendirme panosu
          </h1>
          <p className="max-w-3xl text-sm leading-relaxed text-muted">
            Her sayı ve grafik <code>results/eval_*.jsonl</code>, <code>results/eval_history.jsonl</code> ve{" "}
            <code>results/sadakat_*.jsonl</code> çıktılarından üretilir.{" "}
            {enIyiDogru
              ? `Derin katman değerlendirme seti: ${enIyiDogru.n_ic} kapsam içi + ${enIyiDogru.n_dis} kapsam dışı soru.`
              : null}
          </p>
        </section>

        {enIyiDogru && (
          <section aria-label="Öne çıkan metrikler" className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <div className="flex flex-col justify-between space-y-2 rounded-xl border border-line bg-panel p-4 shadow-xs">
              <div className="text-xs font-medium text-muted">En yüksek doğruluk</div>
              <div>
                <div className="font-serif text-3xl font-semibold tabular-nums text-ink">
                  {yuzde(enIyiDogru.dogru_orani)}
                </div>
                <div className="mt-0.5 text-xs text-muted tabular-nums">
                  {enIyiDogru.dogru}/{enIyiDogru.n_ic} · {kisaModelAdi(enIyiDogru.llm)} + {enIyiDogru.yapilandirma_adi}
                </div>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-panel-soft">
                <div
                  className="h-full rounded-full bg-accent-btn"
                  style={{ width: `${Math.round((enIyiDogru.dogru_orani ?? 0) * 100)}%` }}
                />
              </div>
            </div>

            <div className="flex flex-col justify-between space-y-2 rounded-xl border border-line bg-panel p-4 shadow-xs">
              <div className="text-xs font-medium text-muted">Geçersiz atıf</div>
              <div>
                <div className="font-serif text-3xl font-semibold tabular-nums text-ink">{maxGecersiz ?? "—"}</div>
                <div className="mt-0.5 text-xs font-medium text-ok">
                  {maxGecersiz === 0 ? "Tüm çalıştırmalarda 0 uydurma atıf" : "Çalıştırma bazlı üst sınır"}
                </div>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-ok-bg">
                <div className="h-full w-full rounded-full bg-ok" />
              </div>
            </div>

            <div className="flex flex-col justify-between space-y-2 rounded-xl border border-line bg-panel p-4 shadow-xs">
              <div className="text-xs font-medium text-muted">Kapsam dışı ret</div>
              <div>
                <div className="font-serif text-3xl font-semibold tabular-nums text-ink">
                  {enIyiDogru.dogru_ret}/{enIyiDogru.n_dis}
                </div>
                <div className="mt-0.5 text-xs text-muted">
                  Derin katman kapsam dışı sorularında ({yuzde(enIyiDogru.dogru_ret_orani)})
                </div>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-panel-soft">
                <div
                  className="h-full rounded-full bg-info"
                  style={{ width: `${Math.round((enIyiDogru.dogru_ret_orani ?? 0) * 100)}%` }}
                />
              </div>
            </div>

            <div className="flex flex-col justify-between space-y-2 rounded-xl border border-line bg-panel p-4 shadow-xs">
              <div className="text-xs font-medium text-muted">En yüksek tam destek</div>
              <div>
                <div className="font-serif text-3xl font-semibold tabular-nums text-accent">
                  {enIyiSadakat ? yuzde(enIyiSadakat.sadakat?.tam_destekli_orani) : "—"}
                </div>
                <div className="mt-0.5 text-xs text-muted tabular-nums">
                  {enIyiSadakat?.sadakat
                    ? `${enIyiSadakat.sadakat.tam_destekli}/${enIyiSadakat.sadakat.cevap} (${enIyiSadakat.yapilandirma_adi})`
                    : "Ölçülmedi"}
                </div>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-panel-soft">
                <div
                  className="h-full rounded-full bg-accent-btn"
                  style={{ width: `${Math.round((enIyiSadakat?.sadakat?.tam_destekli_orani ?? 0) * 100)}%` }}
                />
              </div>
            </div>
          </section>
        )}

        <p role="note" className="rounded-xl border border-warn-border bg-warn-bg px-4 py-3 text-xs leading-relaxed text-warn-ink">
          Beklenen cevaplar ve arama altın etiketleri resmî metinle elle doğrulandı (74/74; geliştirici kontrolü, hukukçu incelemesi değildir).{" "}
          <strong>Sadakat:</strong> LLM hakem (<code>claude-haiku-5.5</code>) cevabın her iddiasının atıf yaptığı
          kaynakla desteklenip desteklenmediğini ölçer; <em>tam destekli</em> oranı hem <code>kısmen = 0</code> hem{" "}
          <code>desteksiz = 0</code> olan cevapları sayar (10 kararda 9 elle uyum).
        </p>

        {hata && <p className="text-sm text-warn-ink">{hata}</p>}
        {!veri && !hata && <p className="text-sm text-muted">Değerlendirme verileri yükleniyor…</p>}

        {veri && (
          <>
            <YapilandirmaKarsilastirmasi
              gruplar={veri.yapilandirma_karsilastirmasi}
              rerank={veri.rerank_karsilastirma}
            />
            <ModelTablosu modeller={veri.modeller} />
            <EsikEtkisiKutusu modeller={veri.modeller} />
            <AramaDeneyleri veri={veri.arama_deneyleri} />
            <GenisKatmanBolumu veri={veri.genis_katman} />
            <ZamanGrafigi gecmis={veri.gecmis} />
            <SoruIsiTablosu modeller={veri.modeller} sorular={veri.sorular} />
          </>
        )}
      </div>
    </SiteKabugu>
  );
}
