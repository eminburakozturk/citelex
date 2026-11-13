"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AramaDeneyleri } from "@/components/pano/AramaDeneyleri";
import { EsikEtkisiKutusu } from "@/components/pano/EsikEtkisiKutusu";
import { GenisKatmanBolumu } from "@/components/pano/GenisKatmanBolumu";
import { ModelTablosu } from "@/components/pano/ModelTablosu";
import { SoruIsiTablosu } from "@/components/pano/SoruIsiTablosu";
import { YapilandirmaKarsilastirmasi } from "@/components/pano/YapilandirmaKarsilastirmasi";
import { ZamanGrafigi } from "@/components/pano/ZamanGrafigi";
import { PanoVerisi, tarihSaat } from "@/components/pano/types";

export default function PanoSayfasi() {
  const [veri, setVeri] = useState<PanoVerisi | null>(null);
  const [hata, setHata] = useState<string | null>(null);

  useEffect(() => {
    let iptal = false;
    fetch("/pano.json")
      .then((res) => {
        if (!res.ok) throw new Error("pano.json yüklenemedi.");
        return res.json() as Promise<PanoVerisi>;
      })
      .then((json) => {
        if (!iptal) setVeri(json);
      })
      .catch((e: Error) => {
        if (!iptal) setHata(e.message);
      });
    return () => {
      iptal = true;
    };
  }, []);

  return (
    <div className="min-h-full overflow-x-hidden bg-bg text-ink">
      <header className="guvenli-ust guvenli-yatay border-b border-line bg-panel pb-3">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-x-4 gap-y-1">
          <h1 className="text-lg font-semibold tracking-tight">
            Citelex <span className="font-normal text-muted">· Değerlendirme panosu</span>
          </h1>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted">
            {veri?.uretim_tarihi && <span>Veri: {tarihSaat(veri.uretim_tarihi)}</span>}
            <Link href="/yontem" prefetch={false} className="inline-flex min-h-[40px] items-center text-accent hover:underline">
              Yöntem
            </Link>
            <Link href="/degisiklikler" prefetch={false} className="inline-flex min-h-[40px] items-center text-accent hover:underline">
              Son değişiklikler
            </Link>
            <Link href="/" prefetch={false} className="inline-flex min-h-[40px] items-center text-accent hover:underline">
              ← Soru-cevaba dön
            </Link>
          </div>
        </div>
      </header>

      <main className="guvenli-sayfa-alt guvenli-yatay mx-auto max-w-5xl min-w-0 space-y-8 pt-6">
        <div role="note" className="space-y-1 rounded-md bg-warn-bg px-3 py-2 text-sm text-warn-ink">
          <p>Beklenen cevaplar taslaktır; içerik ölçütü anahtar kelime eşleşmesidir.</p>
          <p className="text-xs opacity-90">
            Sadakat: LLM hakem (claude-haiku-5.5), cevabın her iddiası atıf yaptığı kaynakla destekleniyor mu; elle
            kontrol 10 kararda 9 uyum.
          </p>
        </div>

        {hata && (
          <p className="rounded-md border border-line bg-panel px-3 py-2 text-sm text-accent">{hata}</p>
        )}

        {!veri && !hata && <p className="text-sm text-muted">Değerlendirme verileri yükleniyor…</p>}

        {veri && (
          <>
            <ModelTablosu modeller={veri.modeller} />
            <YapilandirmaKarsilastirmasi
              gruplar={veri.yapilandirma_karsilastirmasi}
              rerank={veri.rerank_karsilastirma}
            />
            <AramaDeneyleri veri={veri.arama_deneyleri} />
            <GenisKatmanBolumu veri={veri.genis_katman} />
            <EsikEtkisiKutusu modeller={veri.modeller} />
            <ZamanGrafigi gecmis={veri.gecmis} />
            <SoruIsiTablosu modeller={veri.modeller} sorular={veri.sorular} />
          </>
        )}
      </main>
    </div>
  );
}
