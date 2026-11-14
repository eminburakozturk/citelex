"use client";

import { useState } from "react";
import { Kaynak, Sonuc, Tur, tarih } from "@/lib/api";
import { SurecZamanCizgisi } from "./SurecZamanCizgisi";

const TUR_ADLARI: Record<Tur, string> = {
  kanun: "Kanun",
  yonetmelik: "Yönetmelik",
  teblig: "Tebliğ",
  karar: "Kurul kararı",
};

const BELGE_TUR_AD: Record<string, string> = {
  kanun: "Kanun",
  yonetmelik: "Yönetmelik",
  teblig: "Tebliğ",
  karar: "Kurul kararı",
};

function AlintiliMetin({
  metin,
  kaynaklar,
  onKaynak,
}: {
  metin: string;
  kaynaklar: Kaynak[];
  onKaynak: (k: Kaynak, tetikleyici: HTMLElement) => void;
}) {
  const byNo = new Map(kaynaklar.map((k) => [k.no, k]));
  const parcalar = metin.split(/(\[\d+\])/g);
  return (
    <div className="font-serif text-[17px] leading-[1.75] text-ink whitespace-pre-wrap">
      {parcalar.map((p, i) => {
        const m = /^\[(\d+)\]$/.exec(p);
        if (!m) return <span key={i}>{p}</span>;
        const no = Number(m[1]);
        const k = byNo.get(no);
        if (!k) return <span key={i}>{p}</span>;
        return (
          <button
            key={i}
            type="button"
            onClick={(e) => onKaynak(k, e.currentTarget)}
            title={k.atif}
            aria-label={`Kaynak ${no}: ${k.atif}`}
            className="mx-0.5 inline-flex min-h-[24px] items-center rounded-md bg-accent-soft px-1.5 py-0.5 align-baseline font-sans text-xs font-semibold text-accent transition-colors hover:bg-accent-btn hover:text-accent-ink"
          >
            [{no}]
          </button>
        );
      })}
    </div>
  );
}

function katmanEtiketi(kanallar?: string[]): string | null {
  if (!kanallar || kanallar.length === 0) return null;
  if (kanallar.includes("genis")) return "Geniş katman (~900 kanun)";
  const adlar = kanallar.map((k) => (k === "mevzuat" ? "Derin mevzuat" : k === "karar" ? "Kurul kararları" : k));
  return adlar.join(" + ");
}

export function CevapKarti({
  sorulan,
  sorulanTurler,
  yukleniyor,
  ajan,
  uzunBekleme,
  akiyor,
  sonuc,
  hata,
  ilgiliSorular,
  onKaynakAc,
  onSoruyuDuzenle,
  onIlgiliSor,
}: {
  sorulan: string;
  sorulanTurler: Tur[] | null;
  yukleniyor: boolean;
  ajan: boolean;
  uzunBekleme: boolean;
  akiyor: string;
  sonuc: Sonuc | null;
  hata: string | null;
  ilgiliSorular: string[];
  onKaynakAc: (k: Kaynak, tetikleyici: HTMLElement) => void;
  onSoruyuDuzenle: (soru: string) => void;
  onIlgiliSor: (soru: string) => void;
}) {
  const [kopyalandi, setKopyalandi] = useState(false);
  const [nasilAcik, setNasilAcik] = useState(false);

  const kaynaklar = sonuc?.kaynaklar ?? [];
  const genisKatman = sonuc?.kanallar?.includes("genis") ?? false;

  async function kopyala() {
    if (!sonuc?.cevap) return;
    try {
      await navigator.clipboard.writeText(sonuc.cevap);
      setKopyalandi(true);
      setTimeout(() => setKopyalandi(false), 1800);
    } catch {
      /* pano erişimi reddedilirse sessiz kal */
    }
  }

  const katman = katmanEtiketi(sonuc?.kanallar);
  const modelAdi = sonuc?.model ?? sonuc?.llm;

  return (
    <section aria-label="Soru ve cevap" className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3 rounded-xl border border-line bg-panel px-4 py-3 shadow-xs">
        <div className="min-w-0 space-y-1.5">
          <div className="text-[11px] font-semibold tracking-wider text-subtle uppercase">Soru</div>
          <p className="text-base font-medium leading-snug text-ink">{sorulan}</p>
          {sorulanTurler && sorulanTurler.length > 0 && sorulanTurler.length < 4 && (
            <div className="flex flex-wrap gap-1.5 pt-0.5">
              {sorulanTurler.map((t) => (
                <span key={t} className="rounded-full bg-panel-soft px-2 py-0.5 text-[11px] font-medium text-muted">
                  {TUR_ADLARI[t] ?? t}
                </span>
              ))}
            </div>
          )}
        </div>
        <button
          type="button"
          onClick={() => onSoruyuDuzenle(sorulan)}
          className="inline-flex min-h-[40px] shrink-0 items-center rounded-lg border border-line bg-bg px-3 py-1.5 text-xs font-medium text-muted transition-colors hover:border-accent hover:text-ink"
        >
          Düzenle
        </button>
      </div>

      <SurecZamanCizgisi
        yukleniyor={yukleniyor}
        ajan={ajan}
        uzunBekleme={uzunBekleme}
        akisBasladi={Boolean(akiyor)}
        sonuc={sonuc}
      />

      {hata && (
        <div role="alert" className="rounded-xl border border-warn-border bg-warn-bg px-4 py-3 text-sm text-warn-ink">
          {hata}
        </div>
      )}

      {(akiyor || sonuc) && (
        <article
          aria-live={yukleniyor ? "polite" : "off"}
          aria-atomic="false"
          className="space-y-4 rounded-xl border border-line bg-panel p-5 shadow-xs"
        >
          {genisKatman && (
            <div role="note" className="space-y-2 rounded-xl border border-warn-border bg-warn-bg px-4 py-3 text-xs text-warn-ink">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="font-semibold">Geniş katman · doğruluğu ölçülmedi</span>
                <span className="rounded-full border border-warn-border bg-panel/70 px-2 py-0.5 text-[11px] font-medium">
                  ~900 kanunluk yedek kanal
                </span>
              </div>
              {sonuc?.uyari && <p className="leading-relaxed">{sonuc.uyari}</p>}
            </div>
          )}

          {sonuc?.bilmiyorum ? (
            <div className="space-y-2 rounded-xl border border-line bg-panel-soft/60 p-4">
              <div className="inline-flex items-center rounded-full bg-panel px-2.5 py-0.5 text-[11px] font-semibold text-muted">
                Yetersiz kaynak / Kapsam dışı
              </div>
              <p className="font-serif text-[17px] leading-relaxed text-ink">{sonuc.cevap}</p>
              {sonuc.neden && <p className="text-xs leading-relaxed text-muted">{sonuc.neden}</p>}
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between gap-2 border-b border-line pb-2.5">
                <span className="text-[11px] font-semibold tracking-wider text-subtle uppercase">
                  Kaynaklı yanıt
                </span>
                {sonuc && (
                  <button
                    type="button"
                    onClick={kopyala}
                    className="inline-flex min-h-[36px] items-center gap-1.5 rounded-lg border border-line bg-bg px-3 py-1 text-xs font-medium text-muted transition-colors hover:border-accent hover:text-ink"
                  >
                    {kopyalandi ? "Kopyalandı ✓" : "Metni kopyala"}
                  </button>
                )}
              </div>

              {akiyor && !sonuc ? (
                <div className="font-serif text-[17px] leading-[1.75] text-ink whitespace-pre-wrap">
                  {akiyor}
                  <span aria-hidden="true" className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-accent align-middle" />
                </div>
              ) : (
                <AlintiliMetin
                  metin={sonuc?.cevap ?? ""}
                  kaynaklar={kaynaklar}
                  onKaynak={onKaynakAc}
                />
              )}
            </div>
          )}

          {sonuc && !genisKatman && sonuc.uyari && (
            <p role="note" className="rounded-lg bg-panel-soft/70 px-3 py-2 text-xs text-muted">
              {sonuc.uyari}
            </p>
          )}
        </article>
      )}

      {sonuc && kaynaklar.length > 0 && (
        <section aria-label="Atıfta bulunulan kaynaklar" className="space-y-2.5">
          <h2 className="px-1 text-xs font-semibold tracking-wider text-subtle uppercase">
            Atıfta bulunulan kaynaklar ({kaynaklar.length})
          </h2>
          <ul className="space-y-2.5">
            {kaynaklar.map((k) => {
              const turAd = BELGE_TUR_AD[k.belge_tur] ?? k.belge_tur;
              return (
                <li key={`${k.no}-${k.anahtar}`}>
                  <button
                    type="button"
                    onClick={(e) => onKaynakAc(k, e.currentTarget)}
                    className="group w-full rounded-xl border border-line bg-panel p-4 text-left shadow-xs transition-all hover:border-accent"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex min-w-0 flex-wrap items-center gap-2">
                        <span className="inline-flex h-6 min-w-6 items-center justify-center rounded-md bg-accent-soft px-1.5 font-sans text-xs font-semibold text-accent">
                          [{k.no}]
                        </span>
                        <span className="font-semibold text-sm text-ink group-hover:text-accent">{k.atif}</span>
                        {turAd && (
                          <span className="rounded-full bg-panel-soft px-2 py-0.5 text-[11px] font-medium text-muted">
                            {turAd}
                          </span>
                        )}
                      </div>
                      <span className="text-xs font-medium text-accent">Maddeyi incele →</span>
                    </div>
                    {k.baslik && <div className="mt-1.5 text-xs font-medium text-muted">{k.baslik}</div>}
                    {k.alinti && (
                      <p className="mt-2 line-clamp-2 border-l-2 border-accent-soft pl-3 font-serif text-sm italic text-muted">
                        &ldquo;{k.alinti}&rdquo;
                      </p>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        </section>
      )}

      {sonuc && (
        <div className="rounded-xl border border-line bg-panel px-4 py-2.5">
          <button
            type="button"
            aria-expanded={nasilAcik}
            onClick={() => setNasilAcik((v) => !v)}
            className="flex min-h-[40px] w-full items-center justify-between text-xs font-medium text-muted transition-colors hover:text-ink"
          >
            <span>Bu cevap nasıl oluştu?</span>
            <span className="text-subtle">{nasilAcik ? "Gizle" : "Göster"}</span>
          </button>

          {nasilAcik && (
            <dl className="mt-2 grid gap-2.5 border-t border-line pt-3 text-xs sm:grid-cols-2 lg:grid-cols-3">
              <div className="rounded-lg bg-bg/70 px-3 py-2">
                <dt className="text-subtle">Gösterilen kaynak</dt>
                <dd className="mt-0.5 font-semibold tabular-nums text-ink">{kaynaklar.length} adet</dd>
              </div>
              {katman && (
                <div className="rounded-lg bg-bg/70 px-3 py-2">
                  <dt className="text-subtle">Katman</dt>
                  <dd className="mt-0.5 font-semibold text-ink">{katman}</dd>
                </div>
              )}
              {modelAdi && (
                <div className="rounded-lg bg-bg/70 px-3 py-2">
                  <dt className="text-subtle">Model</dt>
                  <dd className="mt-0.5 truncate font-semibold text-ink" title={modelAdi}>
                    {modelAdi}
                  </dd>
                </div>
              )}
              {sonuc.sure_sn != null && (
                <div className="rounded-lg bg-bg/70 px-3 py-2">
                  <dt className="text-subtle">Toplam süre</dt>
                  <dd className="mt-0.5 font-semibold tabular-nums text-ink">{sonuc.sure_sn.toFixed(2)} sn</dd>
                </div>
              )}
              {sonuc.arama_sn != null && (
                <div className="rounded-lg bg-bg/70 px-3 py-2">
                  <dt className="text-subtle">Arama süresi</dt>
                  <dd className="mt-0.5 font-semibold tabular-nums text-ink">{sonuc.arama_sn.toFixed(2)} sn</dd>
                </div>
              )}
              {sonuc.llm_sn != null && (
                <div className="rounded-lg bg-bg/70 px-3 py-2">
                  <dt className="text-subtle">LLM süresi</dt>
                  <dd className="mt-0.5 font-semibold tabular-nums text-ink">{sonuc.llm_sn.toFixed(2)} sn</dd>
                </div>
              )}
              {sonuc.gecersiz_atif != null && (
                <div className="rounded-lg bg-bg/70 px-3 py-2">
                  <dt className="text-subtle">Elenen geçersiz atıf</dt>
                  <dd className="mt-0.5 font-semibold tabular-nums text-ink">{sonuc.gecersiz_atif}</dd>
                </div>
              )}
              {sonuc.ajan_deneme != null && (
                <div className="rounded-lg bg-bg/70 px-3 py-2">
                  <dt className="text-subtle">Ajan denemesi</dt>
                  <dd className="mt-0.5 font-semibold tabular-nums text-ink">{sonuc.ajan_deneme}. deneme</dd>
                </div>
              )}
              {sonuc.son_kontrol && (
                <div className="rounded-lg bg-bg/70 px-3 py-2">
                  <dt className="text-subtle">Derlem son kontrol</dt>
                  <dd className="mt-0.5 font-semibold text-ink">{tarih(sonuc.son_kontrol)}</dd>
                </div>
              )}
            </dl>
          )}
        </div>
      )}

      {ilgiliSorular.length > 0 && (
        <section aria-label="İlgili sorular" className="space-y-2.5 pt-1">
          <h2 className="px-1 text-xs font-semibold tracking-wider text-subtle uppercase">İlgili sorular</h2>
          <div className="space-y-2">
            {ilgiliSorular.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => onIlgiliSor(s)}
                className="flex min-h-[44px] w-full items-center justify-between gap-3 rounded-xl border border-line bg-panel px-4 py-2.5 text-left text-sm text-ink shadow-xs transition-colors hover:border-accent hover:bg-panel-soft/60"
              >
                <span>{s}</span>
                <span aria-hidden="true" className="shrink-0 text-muted">→</span>
              </button>
            ))}
          </div>
        </section>
      )}
    </section>
  );
}
