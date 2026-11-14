"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { SiteKabugu } from "@/components/SiteKabugu";
import { CevapKarti } from "@/components/sohbet/CevapKarti";
import { IlkZiyaretRehberi } from "@/components/sohbet/IlkZiyaretRehberi";
import { KaynakPaneli } from "@/components/sohbet/KaynakPaneli";
import {
  GuncellikBilgisi,
  Kaynak,
  KaynakMetni,
  Sonuc,
  Tur,
  guncellikGetir,
  ilgiliGetir,
  kaynakGetir,
  saglik,
  sor,
  tarih,
} from "@/lib/api";

const TURLER: { id: Tur; ad: string }[] = [
  { id: "kanun", ad: "Kanun" },
  { id: "yonetmelik", ad: "Yönetmelik" },
  { id: "teblig", ad: "Tebliğ" },
  { id: "karar", ad: "Kurul kararı" },
];

const ORNEKLER: { konu: string; soru: string; kapsamDisi?: boolean }[] = [
  { konu: "İş hukuku", soru: "Yıllık izin kaç gündür?" },
  { konu: "KVKK", soru: "İşveren çalışanın parmak izini alabilir mi?" },
  { konu: "İSG", soru: "İSG kurulu kaç çalışanda kurulur?" },
  { konu: "Kurul kararı", soru: "Açık rıza hizmet şartına bağlanabilir mi?" },
  { konu: "Geniş katman", soru: "Kira depozitosu en fazla kaç aylık kira olabilir?" },
  {
    konu: "\"Bilmiyorum\" demeyi görün",
    soru: "İstanbul'da bugün hava durumu nasıl?",
    kapsamDisi: true,
  },
];

const AJAN_DEPO = "citelex:ajan";

export default function AnaSayfa() {
  const [girdi, setGirdi] = useState("");
  const [turler, setTurler] = useState<Tur[]>([]);
  const [ajan, setAjan] = useState(true);
  const [ajanBilgiAcik, setAjanBilgiAcik] = useState(false);

  const [sorulan, setSorulan] = useState("");
  const [sorulanTurler, setSorulanTurler] = useState<Tur[] | null>(null);
  const [yukleniyor, setYukleniyor] = useState(false);
  const [uzunBekleme, setUzunBekleme] = useState(false);
  const [akiyor, setAkiyor] = useState("");
  const [sonuc, setSonuc] = useState<Sonuc | null>(null);
  const [hata, setHata] = useState<string | null>(null);
  const [ilgiliSorular, setIlgiliSorular] = useState<string[]>([]);

  const [guncellik, setGuncellik] = useState<GuncellikBilgisi | null>(null);
  const [saglikKontrol, setSaglikKontrol] = useState<string | null>(null);

  const [seciliKaynak, setSeciliKaynak] = useState<{
    anahtar: string;
    atif: string;
    alinti?: string;
  } | null>(null);
  const [kaynakVerisi, setKaynakVerisi] = useState<KaynakMetni | null>(null);
  const [kaynakYukleniyor, setKaynakYukleniyor] = useState(false);
  const [kaynakHata, setKaynakHata] = useState<string | null>(null);

  const abortRef = useRef<AbortController | null>(null);
  const kaynakTetikleyiciRef = useRef<HTMLElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const istekSayaciRef = useRef(0);

  useEffect(() => {
    try {
      const kayit = localStorage.getItem(AJAN_DEPO);
      if (kayit === "0") setAjan(false);
      else if (kayit === "1") setAjan(true);
    } catch {
      /* boş */
    }

    let aktif = true;
    Promise.all([guncellikGetir(), saglik()]).then(([g, s]) => {
      if (!aktif) return;
      if (g) setGuncellik(g);
      if (s?.son_kontrol) setSaglikKontrol(s.son_kontrol);
    });
    return () => {
      aktif = false;
    };
  }, []);

  useEffect(() => {
    if (!yukleniyor || !ajan) {
      setUzunBekleme(false);
      return;
    }
    const timer = setTimeout(() => setUzunBekleme(true), 3000);
    return () => clearTimeout(timer);
  }, [yukleniyor, ajan]);

  function ajanDegistir() {
    setAjan((prev) => {
      const yeni = !prev;
      try {
        localStorage.setItem(AJAN_DEPO, yeni ? "1" : "0");
      } catch {
        /* boş */
      }
      return yeni;
    });
  }

  function turDegistir(t: Tur) {
    setTurler((prev) => (prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]));
  }

  function baslat(soruMetni: string) {
    const temiz = soruMetni.trim();
    if (temiz.length < 3) {
      setHata("Soru en az 3 karakter olmalı.");
      return;
    }
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    const istekId = ++istekSayaciRef.current;

    const aktifTurler = turler.length > 0 && turler.length < 4 ? [...turler] : null;
    setSorulan(temiz);
    setSorulanTurler(aktifTurler);
    setYukleniyor(true);
    setAkiyor("");
    setSonuc(null);
    setHata(null);
    setIlgiliSorular([]);
    setSeciliKaynak(null);

    sor(
      temiz,
      aktifTurler,
      ajan,
      {
        onParca: (m) => setAkiyor((prev) => prev + m),
        onSonuc: (s) => {
          setSonuc(s);
          setYukleniyor(false);
          if (!s.bilmiyorum && s.kaynaklar.length > 0) {
            const anahtarlar = s.kaynaklar.map((k) => k.anahtar).filter(Boolean);
            ilgiliGetir(temiz, anahtarlar).then((liste) => {
              if (istekSayaciRef.current === istekId && liste.length > 0) {
                setIlgiliSorular(liste);
              }
            });
          }
        },
        onHata: (m) => {
          setHata(m);
          setYukleniyor(false);
        },
      },
      ac.signal,
    );
  }

  function formGonder(e: FormEvent) {
    e.preventDefault();
    baslat(girdi);
  }

  function yeniSoru() {
    abortRef.current?.abort();
    setYukleniyor(false);
    setSorulan("");
    setSorulanTurler(null);
    setAkiyor("");
    setSonuc(null);
    setHata(null);
    setIlgiliSorular([]);
    setSeciliKaynak(null);
    inputRef.current?.focus();
  }

  const anahtarlaKaynakAc = useCallback(
    async (anahtar: string, atif = anahtar, alinti?: string, tetikleyici?: HTMLElement) => {
      if (tetikleyici) kaynakTetikleyiciRef.current = tetikleyici;
      setSeciliKaynak({ anahtar, atif, alinti });
      setKaynakVerisi(null);
      setKaynakHata(null);
      setKaynakYukleniyor(true);
      try {
        const veri = await kaynakGetir(anahtar);
        setKaynakVerisi(veri);
      } catch (e) {
        setKaynakHata((e as Error).message || "Kaynak alınamadı.");
      } finally {
        setKaynakYukleniyor(false);
      }
    },
    [],
  );

  const kaynakAc = useCallback(
    (k: Kaynak, tetikleyici: HTMLElement) => {
      anahtarlaKaynakAc(k.anahtar, k.atif, k.alinti, tetikleyici);
    },
    [anahtarlaKaynakAc],
  );

  const panelKapat = useCallback(() => {
    setSeciliKaynak(null);
    requestAnimationFrame(() => kaynakTetikleyiciRef.current?.focus());
  }, []);

  function soruyuDuzenle(metin: string) {
    setGirdi(metin);
    inputRef.current?.focus();
  }

  const sonKontrolTarih = tarih(guncellik?.son_kontrol ?? saglikKontrol);
  const bosDurum = !sorulan;

  return (
    <SiteKabugu
      aktif="sor"
      baslikAlt="KVKK · İş · İSG · Genel Mevzuat"
      ustEk={
        sorulan ? (
          <button
            type="button"
            onClick={yeniSoru}
            className="inline-flex min-h-[40px] items-center rounded-full border border-line bg-panel px-3 py-1 text-xs font-medium text-muted transition-colors hover:border-accent hover:text-ink"
          >
            Yeni soru
          </button>
        ) : undefined
      }
    >
      <div className="space-y-6">
        {bosDurum && <IlkZiyaretRehberi />}

        {bosDurum && (
          <section className="space-y-2 pt-1">
            <div className="text-[11px] font-semibold tracking-wider text-accent uppercase">
              Mevzuat Araştırma Asistanı
            </div>
            <h1 className="font-serif text-3xl font-medium tracking-tight text-ink sm:text-4xl">
              Mevzuata sor, kaynağıyla öğren.
            </h1>
            <p className="max-w-2xl text-sm leading-relaxed text-muted">
              KVKK, İş ve İSG mevzuatı ile KVKK Kurul kararlarında kaynak doğrulamalı arama; eşik altında
              kalınırsa ~900 kanunluk genel derlem taranır.
            </p>
          </section>
        )}

        <form onSubmit={formGonder} className="space-y-3">
          <div className="rounded-xl border border-line bg-panel p-3.5 shadow-xs transition-colors focus-within:border-accent">
            <label htmlFor="soru" className="sr-only">
              Mevzuat sorunuz
            </label>
            <textarea
              ref={inputRef}
              id="soru"
              rows={bosDurum ? 3 : 2}
              value={girdi}
              onChange={(e) => setGirdi(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  baslat(girdi);
                }
              }}
              placeholder="Örn. Yıllık izin süreleri kıdeme göre kaç gündür?"
              className="w-full resize-none bg-transparent text-[15px] leading-relaxed text-ink outline-none placeholder:text-subtle"
              maxLength={500}
            />

            <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-line pt-3">
              <div className="flex flex-wrap items-center gap-1.5" role="group" aria-label="Kaynak türü filtresi">
                {TURLER.map((t) => {
                  const secili = turler.includes(t.id);
                  return (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => turDegistir(t.id)}
                      aria-pressed={secili}
                      className={`min-h-[38px] rounded-full border px-3 py-1 text-xs transition-colors ${
                        secili
                          ? "border-accent bg-accent-soft font-medium text-accent"
                          : "border-line bg-bg text-muted hover:text-ink"
                      }`}
                    >
                      {t.ad}
                    </button>
                  );
                })}
              </div>

              <div className="ml-auto flex items-center gap-2">
                {yukleniyor ? (
                  <button
                    type="button"
                    onClick={() => {
                      abortRef.current?.abort();
                      setYukleniyor(false);
                    }}
                    className="inline-flex min-h-[44px] items-center rounded-lg border border-line bg-bg px-4 py-2 text-xs font-medium text-ink hover:border-accent"
                  >
                    Durdur
                  </button>
                ) : (
                  <button
                    type="submit"
                    className="inline-flex min-h-[44px] items-center gap-1.5 rounded-lg bg-accent-btn px-5 py-2 text-xs font-semibold text-accent-ink transition-colors hover:bg-accent-btn-hover"
                  >
                    <span>Sor</span>
                    <span aria-hidden="true">↑</span>
                  </button>
                )}
              </div>
            </div>

            <div className="mt-2.5 flex flex-wrap items-center justify-between gap-2 border-t border-line/70 pt-2.5 text-xs">
              <div className="flex items-center gap-2.5">
                <span className="text-muted">Derin arama (ajan)</span>
                <button
                  type="button"
                  role="switch"
                  aria-checked={ajan}
                  aria-label="Derin arama (ajan) modu"
                  onClick={ajanDegistir}
                  className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full border p-0.5 transition-colors ${
                    ajan ? "border-accent-btn bg-accent-btn" : "border-line bg-panel-soft"
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 rounded-full bg-white shadow-xs transition-transform ${
                      ajan ? "translate-x-5" : "translate-x-0"
                    }`}
                  />
                </button>
                <button
                  type="button"
                  onClick={() => setAjanBilgiAcik((v) => !v)}
                  aria-expanded={ajanBilgiAcik}
                  aria-label={`${ajan ? "Açık" : "Kapalı"} · Derin arama hakkında bilgi`}
                  className="inline-flex min-h-[32px] items-center rounded-full border border-line px-2 py-0.5 text-[11px] text-muted hover:text-ink"
                >
                  {ajan ? "Açık" : "Kapalı"} · ?
                </button>
              </div>
              <span className="text-[11px] text-subtle">
                {ajan
                  ? "İlk arama eşik altında kalırsa sorguyu yeniden yazar"
                  : "Tek adımda akışlı cevap"}
              </span>
            </div>

            {ajanBilgiAcik && (
              <p className="mt-2 rounded-lg bg-panel-soft/70 px-3 py-2 text-xs leading-relaxed text-muted">
                Ajan modu açıkken yanıt tek parça hâlinde gelir (akış yapılmaz). Ölçülen değerlendirmede
                doğruluğu %80&apos;den %88&apos;e çıkarır; gerektiğinde bir kez sorguyu hukuki terimlerle
                yeniden arar.
              </p>
            )}
          </div>
        </form>

        {bosDurum && (guncellik || sonKontrolTarih) && (
          <section
            aria-label="Derlem güncelliği"
            className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-line bg-panel px-4 py-3 text-xs shadow-xs"
          >
            <div className="flex min-w-0 items-center gap-2.5">
              <span className="relative flex h-2.5 w-2.5 shrink-0">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-ok opacity-60" />
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-ok" />
              </span>
              <div className="min-w-0">
                <div className="font-medium text-ink">
                  {guncellik
                    ? `Derlem güncel · ${guncellik.belge_sayisi} takip edilen belge`
                    : "Derlem çevrimiçi"}
                </div>
                <div className="text-muted">
                  {sonKontrolTarih ? `Son kontrol: ${sonKontrolTarih}` : "Günlük takip etkin"}
                  {guncellik?.rg_bekleyen && guncellik.rg_bekleyen.length > 0 && (
                    <> · Resmî Gazete erken uyarı: {guncellik.rg_bekleyen.length} kayıt</>
                  )}
                </div>
              </div>
            </div>
            <Link
              href="/degisiklikler/"
              prefetch={false}
              className="inline-flex min-h-[36px] shrink-0 items-center rounded-lg border border-line bg-bg px-3 py-1 font-medium text-accent transition-colors hover:border-accent"
            >
              Değişiklikleri gör →
            </Link>
          </section>
        )}

        {bosDurum && (
          <section aria-label="Örnek araştırmalar" className="space-y-2.5">
            <h2 className="px-1 text-xs font-semibold tracking-wider text-subtle uppercase">
              Örnek araştırmalar
            </h2>
            <div className="grid gap-2.5 sm:grid-cols-2">
              {ORNEKLER.map((o) => (
                <button
                  key={o.soru}
                  type="button"
                  onClick={() => {
                    setGirdi(o.soru);
                    baslat(o.soru);
                  }}
                  className="group flex min-h-[68px] flex-col justify-between gap-2 rounded-xl border border-line bg-panel p-3.5 text-left shadow-xs transition-all hover:border-accent"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-[11px] font-medium ${
                        o.kapsamDisi
                          ? "bg-warn-bg text-warn-ink"
                          : "bg-accent-soft text-accent"
                      }`}
                    >
                      {o.konu}
                    </span>
                    <span aria-hidden="true" className="text-xs text-subtle group-hover:text-accent">
                      →
                    </span>
                  </div>
                  <p className="text-sm font-medium leading-snug text-ink">{o.soru}</p>
                </button>
              ))}
            </div>
          </section>
        )}

        {bosDurum && (
          <section aria-label="Neden Citelex" className="rounded-xl border border-line bg-panel p-4 shadow-xs">
            <h2 className="mb-3 text-xs font-semibold tracking-wider text-subtle uppercase">Neden Citelex?</h2>
            <div className="grid gap-3 text-xs leading-relaxed sm:grid-cols-3">
              <div className="space-y-1 rounded-lg bg-bg/70 p-3">
                <div className="font-semibold text-ink">1. Atıfsız cümle yok</div>
                <p className="text-muted">
                  Her ifade numaralı kaynak kartına bağlanır; doğrulamadan geçemeyen uydurma atıf elenir.
                </p>
              </div>
              <div className="space-y-1 rounded-lg bg-bg/70 p-3">
                <div className="font-semibold text-ink">2. Bilmediğini söyler</div>
                <p className="text-muted">
                  Arama skoru eşiği altındaki veya kaynaksız sorularda tahmin yürütmek yerine reddeder.
                </p>
              </div>
              <div className="space-y-1 rounded-lg bg-bg/70 p-3">
                <div className="font-semibold text-ink">3. Güncellik takibi</div>
                <p className="text-muted">
                  Günlük sürüm karşılaştırması ve kelime düzeyinde fark günlüğü ile değişiklikleri izler.
                </p>
              </div>
            </div>
          </section>
        )}

        {sorulan && (
          <CevapKarti
            sorulan={sorulan}
            sorulanTurler={sorulanTurler}
            yukleniyor={yukleniyor}
            ajan={ajan}
            uzunBekleme={uzunBekleme}
            akiyor={akiyor}
            sonuc={sonuc}
            hata={hata}
            ilgiliSorular={ilgiliSorular}
            onKaynakAc={kaynakAc}
            onSoruyuDuzenle={soruyuDuzenle}
            onIlgiliSor={(s) => {
              setGirdi(s);
              baslat(s);
            }}
          />
        )}
      </div>

      {seciliKaynak && (
        <KaynakPaneli
          secili={seciliKaynak}
          veri={kaynakVerisi}
          yukleniyor={kaynakYukleniyor}
          hata={kaynakHata}
          onKapat={panelKapat}
          onAnahtarSec={(yeniAnahtar) => anahtarlaKaynakAc(yeniAnahtar, yeniAnahtar)}
        />
      )}
    </SiteKabugu>
  );
}
