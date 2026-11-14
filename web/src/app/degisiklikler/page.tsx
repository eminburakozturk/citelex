"use client";

import { useEffect, useState } from "react";
import { SiteKabugu } from "@/components/SiteKabugu";
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
import { GuncellikBilgisi, guncellikGetir } from "@/lib/api";

export default function DegisikliklerSayfasi() {
  const [liste, setListe] = useState<DegisiklikKaydi[] | null>(null);
  const [sonKontrol, setSonKontrol] = useState<string | null>(null);
  const [guncellik, setGuncellik] = useState<GuncellikBilgisi | null>(null);
  const [listeHata, setListeHata] = useState<string | null>(null);

  const [seciliId, setSeciliId] = useState<string | null>(null);
  const [ayrinti, setAyrinti] = useState<DegisiklikAyrintisi | null>(null);
  const [ayrintiYukleniyor, setAyrintiYukleniyor] = useState(false);
  const [ayrintiHata, setAyrintiHata] = useState<string | null>(null);

  useEffect(() => {
    let iptal = false;
    Promise.all([degisiklikleriGetir(20), guncellikGetir()])
      .then(([yanit, g]) => {
        if (iptal) return;
        setListe(yanit.degisiklikler);
        setSonKontrol(yanit.son_kontrol ?? g?.son_kontrol ?? null);
        if (g) setGuncellik(g);
        if (yanit.degisiklikler.length > 0) {
          setSeciliId(yanit.degisiklikler[0].fark_id);
        }
      })
      .catch((e: Error) => {
        if (iptal) return;
        setListeHata(e.message);
      });
    return () => {
      iptal = true;
    };
  }, []);

  useEffect(() => {
    if (!seciliId) {
      setAyrinti(null);
      return;
    }
    let iptal = false;
    setAyrintiYukleniyor(true);
    setAyrintiHata(null);
    degisiklikAyrintisiGetir(seciliId)
      .then((d) => {
        if (iptal) return;
        setAyrinti(d);
      })
      .catch((e: Error) => {
        if (iptal) return;
        setAyrintiHata(e.message);
        setAyrinti(null);
      })
      .finally(() => {
        if (!iptal) setAyrintiYukleniyor(false);
      });
    return () => {
      iptal = true;
    };
  }, [seciliId]);

  const gosterilenKontrol = guncellik?.son_kontrol ?? sonKontrol;

  return (
    <SiteKabugu aktif="degisiklikler" genislik="genis" baslikAlt="Mevzuat değişiklik günlüğü">
      <div className="space-y-6">
        <section className="space-y-2">
          <span className="text-[11px] font-semibold tracking-wider text-accent uppercase">
            Otonom Sürüm Takibi
          </span>
          <h1 className="font-serif text-3xl font-medium tracking-tight text-ink">
            Bu madde değişti
          </h1>
          <p className="max-w-3xl text-sm leading-relaxed text-muted">
            Günlük güncelleme hattı ayrıştırılmış metnin özetini (hash) önceki sürümle karşılaştırır; değişen madde veya
            Kurul kararı bölümleri kelime düzeyinde saklanır.
          </p>
        </section>

        {ORNEK_MODU && (
          <p role="note" className="rounded-xl border border-warn-border bg-warn-bg px-4 py-2.5 text-xs text-warn-ink">
            Örnek görünüm etkin (<code>NEXT_PUBLIC_DEGISIKLIK_ORNEK=1</code>): gerçek sürüm deposu yerine{" "}
            <code>web/public/degisiklik_ornek.json</code> gösteriliyor.
          </p>
        )}

        <section aria-label="Takip özeti" className="grid grid-cols-3 gap-3">
          <div className="rounded-xl border border-line bg-panel p-4 shadow-xs">
            <div className="text-[11px] font-semibold tracking-wider text-subtle uppercase">Takip edilen</div>
            <div className="mt-1 font-serif text-2xl font-semibold tabular-nums text-ink">
              {guncellik?.belge_sayisi != null ? `${guncellik.belge_sayisi}` : "—"}
            </div>
            <div className="text-xs text-muted">
              {guncellik?.belge_sayisi != null ? "belge" : "Derin + geniş"}
            </div>
          </div>

          <div className="rounded-xl border border-line bg-panel p-4 shadow-xs">
            <div className="flex items-center justify-between gap-1 text-[11px] font-semibold tracking-wider text-subtle uppercase">
              <span>Son kontrol</span>
              <span className="h-2 w-2 rounded-full bg-ok" aria-hidden="true" />
            </div>
            <div className="mt-1 text-sm font-medium text-ink">
              {gosterilenKontrol ? zamanMetni(gosterilenKontrol) : "—"}
            </div>
            <div className="text-xs text-muted">İçerik hash karşılaştırması</div>
          </div>

          <div className="rounded-xl border border-line bg-panel p-4 shadow-xs">
            <div className="text-[11px] font-semibold tracking-wider text-subtle uppercase">Değişiklik</div>
            <div className="mt-1 font-serif text-2xl font-semibold tabular-nums text-accent">
              {liste ? liste.filter((k) => !k.test).length : "—"}
            </div>
            <div className="text-xs text-muted">
              gerçek değişiklik
              {liste && liste.some((k) => k.test) ? ` · ${liste.filter((k) => k.test).length} test kaydı` : ""}
            </div>
          </div>
        </section>

        {guncellik && (
          <section
            aria-label="Resmî Gazete erken uyarı"
            className="space-y-3 rounded-xl border border-line bg-panel p-4 shadow-xs"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-sm font-semibold text-ink">Resmî Gazete erken uyarı</h2>
              <span
                className={`rounded-full px-2.5 py-0.5 text-[11px] font-semibold ${
                  guncellik.rg_bekleyen.length === 0 ? "bg-ok-bg text-ok" : "bg-warn-bg text-warn-ink"
                }`}
              >
                {guncellik.rg_bekleyen.length === 0
                  ? "Bekleyen yok"
                  : `${guncellik.rg_bekleyen.length} bekleyen kayıt`}
              </span>
            </div>

            {guncellik.rg_bekleyen.length === 0 ? (
              <p className="rounded-lg bg-ok-bg/70 px-3 py-2 text-xs font-medium text-ok">
                Resmî Gazete&apos;de derlemdeki belgelerle eşleşen işlenmemiş değişiklik görünmüyor.
              </p>
            ) : (
              <ul className="space-y-2">
                {guncellik.rg_bekleyen.map((r, i) => (
                  <li
                    key={`${r.belge_id}-${i}`}
                    className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-warn-border bg-warn-bg/60 px-3 py-2 text-xs"
                  >
                    <div className="min-w-0 space-y-0.5">
                      <div className="font-medium text-ink">{r.baslik}</div>
                      <div className="text-muted">
                        {r.gun} · <code>{r.belge_id}</code>
                      </div>
                    </div>
                    {r.url && (
                      <a
                        href={r.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium text-accent underline"
                      >
                        RG aç ↗
                      </a>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}

        {listeHata && (
          <p role="alert" className="rounded-xl border border-warn-border bg-warn-bg px-4 py-3 text-xs text-warn-ink">
            {listeHata}
          </p>
        )}

        {!liste && !listeHata && <p className="text-sm text-muted">Değişiklik kayıtları yükleniyor…</p>}

        {liste && liste.length === 0 && (
          <section className="rounded-xl border border-line bg-panel p-6 text-sm text-muted shadow-xs">
            Henüz kayıtlı bir değişiklik yok. Takip edilen belgelerden biri değiştiğinde eski ve yeni sürümün madde/bölüm
            düzeyindeki farkı burada listelenir.
          </section>
        )}

        {liste && liste.length > 0 && (
          <div className="grid gap-5 lg:grid-cols-[20rem_1fr] lg:items-start">
            <aside aria-label="Değişiklik kayıtları" className="space-y-2.5">
              <div className="px-1 text-xs font-medium text-muted">Kayıtlar ({liste.length})</div>
              <ul className="space-y-2.5">
                {liste.map((k) => {
                  const secili = k.fark_id === seciliId;
                  const toplam = k.ozet.degisti + k.ozet.eklendi + k.ozet.silindi;
                  return (
                    <li key={k.fark_id}>
                      <button
                        type="button"
                        onClick={() => setSeciliId(k.fark_id)}
                        aria-current={secili ? "true" : undefined}
                        className={`w-full rounded-xl border p-3.5 text-left shadow-xs transition-colors ${
                          secili
                            ? "border-accent bg-panel"
                            : "border-line bg-panel/80 hover:border-accent/50"
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <span className="font-serif text-base font-medium break-words text-ink">
                            {belgeBasligi(k.doc_key, k.belge_id)}
                          </span>
                          <span className="shrink-0 rounded-full bg-panel-soft px-2 py-0.5 text-[11px] text-muted">
                            {turAdi(k.tur)}
                          </span>
                        </div>
                        <div className="mt-1 text-xs text-muted">{zamanMetni(k.zaman)}</div>
                        <div className="mt-2 flex flex-wrap gap-1.5 text-[11px] tabular-nums">
                          {k.test && (
                            <span className="rounded-full border border-line px-2 py-0.5 font-medium text-muted">
                              Test kaydı
                            </span>
                          )}
                          {k.ozet.degisti > 0 && (
                            <span className="rounded-full bg-warn-bg px-2 py-0.5 font-medium text-warn-ink">
                              {k.ozet.degisti} değişti
                            </span>
                          )}
                          {k.ozet.eklendi > 0 && (
                            <span className="rounded-full bg-ok-bg px-2 py-0.5 font-medium text-ok">
                              {k.ozet.eklendi} eklendi
                            </span>
                          )}
                          {k.ozet.silindi > 0 && (
                            <span className="rounded-full bg-accent-soft px-2 py-0.5 font-medium text-accent">
                              {k.ozet.silindi} silindi
                            </span>
                          )}
                          {toplam === 0 && <span className="text-muted">Fark yok</span>}
                        </div>
                        {k.birimler.length > 0 && (
                          <div className="mt-1.5 truncate text-[11px] text-muted">
                            {k.birimler.map((b) => birimEtiketi(b.etiket)).join(", ")}
                          </div>
                        )}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </aside>

            <div className="min-w-0">
              {ayrintiYukleniyor && <p className="text-sm text-muted">Fark yükleniyor…</p>}
              {ayrintiHata && (
                <p role="alert" className="rounded-xl border border-warn-border bg-warn-bg px-4 py-3 text-xs text-warn-ink">
                  {ayrintiHata}
                </p>
              )}
              {ayrinti && !ayrintiYukleniyor && <DegisiklikAyrinti veri={ayrinti} />}
            </div>
          </div>
        )}
      </div>
    </SiteKabugu>
  );
}
