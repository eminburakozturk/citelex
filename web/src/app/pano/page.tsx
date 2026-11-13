"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { EsikEtkisiKutusu } from "@/components/pano/EsikEtkisiKutusu";
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
    <div className="min-h-full bg-bg text-ink">
      <header className="border-b border-line bg-panel px-4 py-3">
        <div className="mx-auto flex max-w-5xl flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
          <h1 className="text-lg font-semibold tracking-tight">
            Citelex <span className="font-normal text-muted">· Değerlendirme panosu</span>
          </h1>
          <div className="flex flex-wrap items-baseline gap-4 text-xs text-muted">
            {veri?.uretim_tarihi && <span>Veri: {tarihSaat(veri.uretim_tarihi)}</span>}
            <Link href="/degisiklikler" className="text-accent hover:underline">
              Son değişiklikler
            </Link>
            <Link href="/" className="text-accent hover:underline">
              ← Soru-cevaba dön
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-8 px-4 py-6">
        <div className="space-y-1 rounded-md bg-warn-bg px-3 py-2 text-sm text-warn-ink">
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
            <EsikEtkisiKutusu modeller={veri.modeller} />
            <ZamanGrafigi gecmis={veri.gecmis} />
            <SoruIsiTablosu modeller={veri.modeller} sorular={veri.sorular} />
          </>
        )}
      </main>
    </div>
  );
}
