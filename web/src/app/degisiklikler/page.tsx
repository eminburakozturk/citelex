"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { tarih } from "@/lib/api";
import { DegisiklikAyrinti } from "@/components/degisiklik/DegisiklikAyrinti";
import {
  DegisiklikAyrintisi,
  DegisiklikKaydi,
  ORNEK_MODU,
  belgeBasligi,
  birimEtiketi,
  degisiklikAyrintisiGetir,
  degisiklikleriGetir,
  turAdi,
  zamanMetni,
} from "@/components/degisiklik/types";

export default function DegisikliklerSayfasi() {
  const [liste, setListe] = useState<DegisiklikKaydi[] | null>(null);
  const [sonKontrol, setSonKontrol] = useState<string | null>(null);
  const [listeHata, setListeHata] = useState<string | null>(null);
  const [seciliId, setSeciliId] = useState<string | null>(null);
  const [ayrinti, setAyrinti] = useState<DegisiklikAyrintisi | null>(null);
  const [ayrintiHata, setAyrintiHata] = useState<string | null>(null);
  const [ayrintiYukleniyor, setAyrintiYukleniyor] = useState(false);

  useEffect(() => {
    let iptal = false;
    degisiklikleriGetir(20)
      .then((res) => {
        if (iptal) return;
        setListe(res.degisiklikler);
        setSonKontrol(res.son_kontrol ?? null);
        if (res.degisiklikler.length > 0) {
          setSeciliId(res.degisiklikler[0].fark_id);
        }
      })
      .catch((e: Error) => {
        if (!iptal) setListeHata(e.message);
      });
    return () => {
      iptal = true;
    };
  }, []);

  useEffect(() => {
    if (!seciliId) return;
    let iptal = false;
    setAyrintiYukleniyor(true);
    setAyrintiHata(null);
    degisiklikAyrintisiGetir(seciliId)
      .then((d) => {
        if (!iptal) {
          setAyrinti(d);
          setAyrintiYukleniyor(false);
        }
      })
      .catch((e: Error) => {
        if (!iptal) {
          setAyrinti(null);
          setAyrintiHata(e.message);
          setAyrintiYukleniyor(false);
        }
      });
    return () => {
      iptal = true;
    };
  }, [seciliId]);

  return (
    <div className="min-h-full bg-bg text-ink">
      <header className="border-b border-line bg-panel px-4 py-3">
        <div className="mx-auto flex max-w-5xl flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
          <h1 className="text-lg font-semibold tracking-tight">
            Citelex <span className="font-normal text-muted">· Son değişiklikler</span>
          </h1>
          <div className="flex flex-wrap items-baseline gap-4 text-xs text-muted">
            <span>Son kontrol: {tarih(sonKontrol)}</span>
            <Link href="/pano" className="text-accent hover:underline">
              Değerlendirme panosu
            </Link>
            <Link href="/" className="text-accent hover:underline">
              ← Soru-cevaba dön
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-6 px-4 py-6">
        <div className="flex flex-wrap items-center justify-between gap-2 rounded-md bg-warn-bg px-3 py-2 text-sm text-warn-ink">
          <p>
            Kaynak kontrollerinde tespit edilen sürüm farkları madde veya bölüm düzeyinde listelenir. Eski sürümler
            saklanır.
          </p>
          {ORNEK_MODU && (
            <span className="rounded border border-warn-ink/30 px-2 py-0.5 text-xs font-medium">
              Örnek veri (data/store/farklar)
            </span>
          )}
        </div>

        {listeHata && (
          <p className="rounded-md border border-line bg-panel px-3 py-2 text-sm text-accent">{listeHata}</p>
        )}

        {!liste && !listeHata && <p className="text-sm text-muted">Değişiklik kayıtları yükleniyor…</p>}

        {liste && liste.length === 0 && (
          <div className="rounded-lg border border-line bg-panel p-6 text-sm text-muted">
            Henüz kaydedilmiş mevzuat veya karar değişikliği yok.
          </div>
        )}

        {liste && liste.length > 0 && (
          <div className="space-y-6">
            <section aria-label="Değişiklik listesi" className="grid gap-3 md:grid-cols-2">
              {liste.map((k) => {
                const secili = seciliId === k.fark_id;
                return (
                  <button
                    key={k.fark_id}
                    type="button"
                    onClick={() => setSeciliId(k.fark_id)}
                    aria-pressed={secili}
                    className={`rounded-lg border p-3.5 text-left transition-colors ${
                      secili ? "border-accent bg-accent-soft/40" : "border-line bg-panel hover:border-accent/60"
                    }`}
                  >
                    <div className="flex flex-wrap items-baseline justify-between gap-2">
                      <span className="font-semibold text-ink">{belgeBasligi(k.doc_key, k.belge_id)}</span>
                      <span className="text-xs text-muted">{turAdi(k.tur)}</span>
                    </div>
                    <p className="mt-1 text-xs text-muted">{zamanMetni(k.zaman)}</p>
                    <div className="mt-2.5 flex flex-wrap gap-1.5 text-xs">
                      {k.ozet.degisti > 0 && (
                        <span className="rounded bg-warn-bg px-2 py-0.5 text-warn-ink">
                          {k.ozet.degisti} değişti
                        </span>
                      )}
                      {k.ozet.eklendi > 0 && (
                        <span className="rounded bg-emerald-500/15 px-2 py-0.5 text-emerald-700 dark:text-emerald-300">
                          {k.ozet.eklendi} eklendi
                        </span>
                      )}
                      {k.ozet.silindi > 0 && (
                        <span className="rounded bg-accent-soft px-2 py-0.5 text-accent">
                          {k.ozet.silindi} silindi
                        </span>
                      )}
                      <span className="text-muted">
                        · {k.birimler.map((b) => birimEtiketi(b.etiket)).join(", ")}
                      </span>
                    </div>
                  </button>
                );
              })}
            </section>

            {ayrintiYukleniyor && <p className="text-sm text-muted">Değişiklik ayrıntısı yükleniyor…</p>}
            {ayrintiHata && (
              <p className="rounded-md border border-line bg-panel px-3 py-2 text-sm text-accent">{ayrintiHata}</p>
            )}
            {!ayrintiYukleniyor && ayrinti && <DegisiklikAyrinti veri={ayrinti} />}
          </div>
        )}
      </main>
    </div>
  );
}
