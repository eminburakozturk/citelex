"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Kaynak, KaynakMetni, Sonuc, Tur, kaynakGetir, saglik, sor, tarih } from "@/lib/api";

const TURLER: { id: Tur; ad: string }[] = [
  { id: "kanun", ad: "Kanun" },
  { id: "yonetmelik", ad: "Yönetmelik" },
  { id: "teblig", ad: "Tebliğ" },
  { id: "karar", ad: "KVKK Kurul kararı" },
];
const TUR_ADI: Record<Tur, string> = { kanun: "Kanun", yonetmelik: "Yönetmelik", teblig: "Tebliğ", karar: "Kurul kararı" };
const ORNEKLER = [
  "Yıllık ücretli izin süresi kaç gündür?",
  "İşveren çalışanın kurumsal e-postasını izleyebilir mi?",
  "İş kazası Sosyal Güvenlik Kurumuna kaç gün içinde bildirilir?",
  "Veri ihlali Kurula ne kadar sürede bildirilmelidir?",
  "Kira sözleşmesinde kiracıdan alınan güvence (depozito) en fazla ne kadar olabilir?",
];
const BOLUM_ADI: Record<string, string> = {
  sikayet: "Şikâyet / ihlal bildirimi",
  savunma: "Veri sorumlusunun savunması",
  degerlendirme: "Kurulun değerlendirmesi",
  hukum: "Kurulun kararı",
};

interface Mesaj {
  id: number;
  soru: string;
  metin: string; // akış sırasında biriken, bitince doğrulanmış cevap
  baglam: Kaynak[]; // [n] -> kaynak (akış sırasında)
  ajan?: boolean;
  sonuc?: Sonuc;
  hata?: string;
  suruyor: boolean;
}

const AJAN_ANAHTAR = "citelex:ajan";

export default function Sayfa() {
  const [mesajlar, setMesajlar] = useState<Mesaj[]>([]);
  const [girdi, setGirdi] = useState("");
  const [secili, setSecili] = useState<Tur[]>(TURLER.map((t) => t.id));
  const [ajan, setAjan] = useState(true);
  const [sonKontrol, setSonKontrol] = useState<string | null>(null);
  const [panel, setPanel] = useState<{ anahtar: string; veri?: KaynakMetni; hata?: string } | null>(null);
  const son = useRef<HTMLDivElement>(null);
  const sayac = useRef(0);
  const tetikleyiciRef = useRef<HTMLElement | null>(null);
  const mesgul = mesajlar.some((m) => m.suruyor);

  useEffect(() => {
    try {
      const kayit = window.localStorage.getItem(AJAN_ANAHTAR);
      if (kayit === "0" || kayit === "false") setAjan(false);
      else if (kayit === "1" || kayit === "true") setAjan(true);
    } catch {}
    saglik().then((s) => setSonKontrol(s?.son_kontrol ?? null));
  }, []);
  useEffect(() => {
    son.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [mesajlar]);

  function ajanDegistir(yeni: boolean) {
    setAjan(yeni);
    try {
      window.localStorage.setItem(AJAN_ANAHTAR, yeni ? "1" : "0");
    } catch {}
  }

  function guncelle(id: number, f: (m: Mesaj) => Mesaj) {
    setMesajlar((ms) => ms.map((m) => (m.id === id ? f(m) : m)));
  }

  async function gonder(soru: string) {
    soru = soru.trim();
    if (soru.length < 3 || mesgul || secili.length === 0) return;
    const id = ++sayac.current;
    const ajanAcik = ajan;
    setGirdi("");
    setMesajlar((ms) => [...ms, { id, soru, metin: "", baglam: [], ajan: ajanAcik, suruyor: true }]);
    await sor(
      soru,
      secili.length === TURLER.length ? null : secili,
      {
        baglam: (k) => guncelle(id, (m) => ({ ...m, baglam: k })),
        parca: (t) => guncelle(id, (m) => ({ ...m, metin: m.metin + t })),
        // Doğrulanmış cevap esas alınır: atıf doğrulamasından geçemeyen metin burada "bilmiyorum" ile değişir.
        sonuc: (s) => guncelle(id, (m) => ({ ...m, sonuc: s, baglam: s.kaynaklar, metin: s.cevap, suruyor: false })),
        hata: (h) => guncelle(id, (m) => ({ ...m, hata: h, suruyor: false })),
      },
      undefined,
      ajanAcik
    );
    guncelle(id, (m) => ({ ...m, suruyor: false }));
  }

  async function kaynakAc(anahtar: string) {
    if (typeof document !== "undefined" && document.activeElement instanceof HTMLElement) {
      tetikleyiciRef.current = document.activeElement;
    }
    setPanel({ anahtar });
    try {
      const veri = await kaynakGetir(anahtar);
      setPanel((p) => (p?.anahtar === anahtar ? { anahtar, veri } : p));
    } catch (e) {
      setPanel((p) => (p?.anahtar === anahtar ? { anahtar, hata: (e as Error).message } : p));
    }
  }

  function kaynakKapat() {
    setPanel(null);
    const hedef = tetikleyiciRef.current;
    tetikleyiciRef.current = null;
    if (hedef) {
      window.requestAnimationFrame(() => hedef.focus());
    }
  }

  return (
    <div className="flex h-dvh overflow-x-hidden">
      <main className="flex min-w-0 flex-1 flex-col">
        <header className="guvenli-ust guvenli-yatay border-b border-line bg-panel pb-3">
          <div className="mx-auto flex max-w-3xl flex-wrap items-center justify-between gap-x-4 gap-y-1">
            <h1 className="text-lg font-semibold tracking-tight">
              Citelex <span className="font-normal text-muted">· kaynak gösteren mevzuat asistanı</span>
            </h1>
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted">
              <p>Kaynakların son kontrolü: {tarih(sonKontrol)}</p>
              <Link href="/yontem" prefetch={false} className="inline-flex min-h-[40px] items-center text-accent hover:underline">
                Yöntem
              </Link>
              <Link href="/pano" prefetch={false} className="inline-flex min-h-[40px] items-center text-accent hover:underline">
                Değerlendirme panosu
              </Link>
              <Link href="/degisiklikler" prefetch={false} className="inline-flex min-h-[40px] items-center text-accent hover:underline">
                Son değişiklikler
              </Link>
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="mx-auto max-w-3xl space-y-6">
            <p role="note" className="rounded-md bg-warn-bg px-3 py-2 text-sm text-warn-ink">
              Bu sistem hukuki tavsiye vermez. Cevaplar yalnızca gösterilen kaynak metinlere dayanır; karar vermeden önce
              kaynağın kendisini okuyun.
            </p>

            {mesajlar.length === 0 && (
              <section>
                <p className="mb-3 text-sm text-muted">
                  KVKK, İş Kanunu, İSG Kanunu, ilgili yönetmelik ve tebliğler ile seçilmiş 40 KVKK Kurul kararı üzerine soru
                  sorabilirsiniz. Kapsam dışındaki sorularda sistem “bilmiyorum” der.
                </p>
                <div className="grid gap-2 sm:grid-cols-2">
                  {ORNEKLER.map((o, idx) => (
                    <button
                      key={o}
                      onClick={() => gonder(o)}
                      className={`min-h-[44px] rounded-md border border-line bg-panel px-3 py-2.5 text-left text-sm hover:border-accent ${
                        ORNEKLER.length % 2 === 1 && idx === ORNEKLER.length - 1 ? "sm:col-span-2" : ""
                      }`}
                    >
                      {o}
                    </button>
                  ))}
                </div>
              </section>
            )}

            {mesajlar.map((m) => (
              <article key={m.id} className="space-y-3">
                <p className="ml-auto w-fit max-w-[85%] break-words rounded-lg bg-accent-soft px-3 py-2 text-sm">
                  {m.soru}
                </p>
                <Cevap m={m} ac={kaynakAc} />
              </article>
            ))}
            <div ref={son} />
          </div>
        </div>

        <footer className="guvenli-alt guvenli-yatay border-t border-line bg-panel pt-3">
          <form
            className="mx-auto max-w-3xl space-y-2.5"
            onSubmit={(e) => {
              e.preventDefault();
              gonder(girdi);
            }}
          >
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="mr-1 text-muted">Kaynak türü:</span>
                {TURLER.map((t) => {
                  const acik = secili.includes(t.id);
                  return (
                    <button
                      key={t.id}
                      type="button"
                      aria-pressed={acik}
                      onClick={() => setSecili((s) => (acik ? s.filter((x) => x !== t.id) : [...s, t.id]))}
                      className={`inline-flex min-h-[40px] items-center rounded-full border px-3 py-1.5 ${acik ? "border-accent bg-accent-soft text-ink" : "border-line text-muted"}`}
                    >
                      {t.ad}
                    </button>
                  );
                })}
                {secili.length === 0 && <span className="text-accent">En az bir tür seçin.</span>}
              </div>

              <button
                type="button"
                role="switch"
                aria-checked={ajan}
                onClick={() => ajanDegistir(!ajan)}
                className={`inline-flex min-h-[40px] items-center gap-2 rounded-full border px-3 py-1.5 transition-colors ${
                  ajan ? "border-accent bg-accent-soft text-ink" : "border-line bg-bg text-muted"
                }`}
              >
                <span
                  aria-hidden="true"
                  className={`inline-block h-2.5 w-2.5 rounded-full ${ajan ? "bg-accent" : "bg-muted/50"}`}
                />
                <span>Derin arama (ajan)</span>
                <span className="text-[11px] font-medium">{ajan ? "Açık" : "Kapalı"}</span>
              </button>
            </div>
            <div className="flex gap-2">
              <input
                value={girdi}
                onChange={(e) => setGirdi(e.target.value)}
                maxLength={500}
                placeholder="Sorunuzu yazın…"
                aria-label="Soru"
                className="min-h-[44px] min-w-0 flex-1 rounded-md border border-line bg-bg px-3 py-2 text-sm focus:border-accent"
              />
              <button
                type="submit"
                disabled={mesgul || girdi.trim().length < 3 || secili.length === 0}
                className="min-h-[44px] shrink-0 rounded-md bg-accent px-4 py-2 text-sm font-medium text-bg disabled:opacity-40"
              >
                {mesgul ? "Yanıtlanıyor…" : "Sor"}
              </button>
            </div>
          </form>
        </footer>
      </main>

      {panel && <KaynakPaneli panel={panel} kapat={kaynakKapat} />}
    </div>
  );
}

function Cevap({ m, ac }: { m: Mesaj; ac: (anahtar: string) => void }) {
  const [uzunBekleme, setUzunBekleme] = useState(false);

  useEffect(() => {
    if (!m.suruyor || m.metin || !m.ajan) {
      setUzunBekleme(false);
      return;
    }
    const timer = window.setTimeout(() => setUzunBekleme(true), 3000);
    return () => window.clearTimeout(timer);
  }, [m.suruyor, m.metin, m.ajan]);

  if (m.hata) return <p className="rounded-md border border-line bg-panel px-3 py-2 text-sm text-accent">{m.hata}</p>;
  const s = m.sonuc;
  const genis = s?.kanallar?.includes("genis") ?? false;
  // [n] -> kaynak: bitince doğrudan sonuc.kaynaklar'dan (ajan modunda baglam gelmez), akış sırasında baglam'dan
  const bul = (n: number) =>
    s ? s.kaynaklar.find((k) => k.no === n) : m.baglam.find((k) => k.no === n) ?? m.baglam[n - 1];
  return (
    <div
      aria-live="polite"
      aria-busy={m.suruyor}
      className="rounded-lg border border-line bg-panel px-4 py-3 text-[15px] leading-relaxed"
    >
      {!m.metin && m.suruyor && (
        <div className="space-y-1">
          <p className="text-sm text-muted">Kaynaklar aranıyor…</p>
          {m.ajan && uzunBekleme && (
            <p className="text-xs text-muted">Gerekirse soru yeniden yazılıp tekrar aranıyor…</p>
          )}
        </div>
      )}
      {genis && (
        <div className="mb-3 space-y-1.5 border-b border-line pb-2.5">
          <span
            role="note"
            className="inline-flex items-center rounded-md border border-warn-ink/30 bg-warn-bg px-2.5 py-1 text-xs font-medium text-warn-ink"
          >
            Geniş katman · doğruluğu ölçülmedi
          </span>
          {s?.uyari && (
            <p role="note" className="text-xs leading-relaxed text-muted">
              {s.uyari}
            </p>
          )}
        </div>
      )}
      {m.metin && (
        <p className="whitespace-pre-wrap break-words">
          {m.metin.split(/(\[\d{1,2}\])/).map((parca, i) => {
            const no = /^\[(\d{1,2})\]$/.exec(parca)?.[1];
            const k = no ? bul(Number(no)) : undefined;
            if (!no) return <span key={i}>{parca}</span>;
            if (!k) return null; // doğrulanamayan atıf gösterilmez
            return (
              <button
                key={i}
                type="button"
                onClick={() => ac(k.anahtar)}
                title={k.atif}
                aria-label={`Kaynak ${no}: ${k.atif}`}
                className="mx-0.5 rounded bg-accent-soft px-1.5 py-0.5 align-baseline text-xs font-medium text-accent hover:underline"
              >
                {no}
              </button>
            );
          })}
        </p>
      )}
      {s?.bilmiyorum && s.neden && <p className="mt-1 text-sm text-muted">{s.neden}</p>}
      {s?.ajan_deneme === 2 && (
        <details className="mt-3 border-t border-line pt-2 text-xs text-muted">
          <summary className="flex min-h-[40px] cursor-pointer select-none items-center hover:text-ink">
            {s.bilmiyorum
              ? "Soru yeniden yazılıp tekrar arandı; yine yeterli kaynak bulunamadı."
              : "Soru yeniden yazılarak tekrar arandı (2. deneme)"}
          </summary>
          <p className="mt-1 break-words rounded bg-bg px-2.5 py-2 text-ink">
            {s.bilmiyorum ? "Denenen arama sorgusu: " : "İlk aramada yeterli kaynak bulunamadı; soru şu sorguyla yeniden arandı: "}
            <span className="font-medium">{s.ajan_sorgular?.[0] ?? "—"}</span>
          </p>
        </details>
      )}
      {s && s.kaynaklar.length > 0 && (
        <ul className="mt-3 space-y-1 border-t border-line pt-2 text-sm">
          {s.kaynaklar.map((k) => (
            <li key={k.no}>
              <button
                type="button"
                onClick={() => ac(k.anahtar)}
                className="flex min-h-[40px] w-full items-start gap-2 rounded py-1.5 text-left hover:bg-bg/70"
              >
                <span className="mt-0.5 w-5 shrink-0 text-right text-xs font-medium text-accent">{k.no}</span>
                <span className="min-w-0 flex-1 break-words">
                  <span className="hover:underline">{k.atif}</span>
                  {k.baslik ? <span className="text-muted"> — {k.baslik}</span> : null}
                  <span className="ml-2 text-xs text-muted">{TUR_ADI[k.belge_tur]}</span>
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function KaynakPaneli({ panel, kapat }: { panel: { anahtar: string; veri?: KaynakMetni; hata?: string }; kapat: () => void }) {
  const v = panel.veri;
  const panelRef = useRef<HTMLElement>(null);
  const kapatRef = useRef(kapat);
  useEffect(() => {
    kapatRef.current = kapat;
  });
  useEffect(() => {
    panelRef.current?.focus();
    const f = (e: KeyboardEvent) => {
      if (e.key === "Escape") kapatRef.current();
    };
    window.addEventListener("keydown", f);
    return () => window.removeEventListener("keydown", f);
  }, []);
  return (
    <div
      className="fixed inset-0 z-20 flex flex-col justify-end bg-black/40 md:static md:z-auto md:block md:bg-transparent"
      onClick={(e) => {
        if (e.target === e.currentTarget) kapat();
      }}
    >
      <aside
        ref={panelRef}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-labelledby="kaynak-panel-baslik"
        className="flex max-h-[82dvh] w-full flex-col rounded-t-2xl border-t border-line bg-panel shadow-xl md:h-full md:max-h-none md:w-[26rem] md:shrink-0 md:rounded-none md:border-l md:border-t-0 md:shadow-none lg:w-[32rem]"
      >
        <div className="flex justify-center pt-2 pb-1 md:hidden" aria-hidden="true">
          <span className="h-1 w-10 rounded-full bg-line" />
        </div>
        <div className="flex items-start justify-between gap-3 border-b border-line px-4 py-3">
          <div className="min-w-0">
            <h2 id="kaynak-panel-baslik" className="break-words font-semibold">
              {v?.atif ?? "Kaynak"}
            </h2>
            {v?.baslik && <p className="break-words text-sm text-muted">{v.baslik}</p>}
          </div>
          <button
            type="button"
            onClick={kapat}
            aria-label="Kaynak panelini kapat"
            className="inline-flex min-h-[40px] min-w-[44px] shrink-0 items-center justify-center rounded border border-line px-3 py-1.5 text-sm"
          >
            Kapat
          </button>
        </div>
        <div className="guvenli-panel-alt flex-1 space-y-4 overflow-y-auto px-4 pt-4">
          {!v && !panel.hata && <p className="text-sm text-muted">Yükleniyor…</p>}
          {panel.hata && <p className="text-sm text-accent">{panel.hata}</p>}
          {v && (
            <>
              <p className="text-xs text-muted">
                {v.belge_adi}
                {v.karar_tarihi ? ` · ${v.karar_tarihi}` : ""}
              </p>
              {v.mulga && (
                <p role="note" className="rounded bg-warn-bg px-2 py-1 text-sm text-warn-ink">
                  Bu hüküm yürürlükten kaldırılmıştır.
                </p>
              )}
              <div className="kanun-metni space-y-3 text-[15px]">
                {v.parcalar.map((p, i) => (
                  <div key={i} className={p.mulga ? "text-muted" : ""}>
                    {p.bolum && (i === 0 || v.parcalar[i - 1].bolum !== p.bolum) && (
                      <h3 className="mb-1 font-sans text-xs font-semibold uppercase tracking-wide text-muted">
                        {BOLUM_ADI[p.bolum] ?? p.bolum}
                      </h3>
                    )}
                    <p className="whitespace-pre-wrap break-words">{p.metin}</p>
                  </div>
                ))}
              </div>
              {v.dipnotlar.length > 0 && (
                <details className="text-sm text-muted">
                  <summary className="flex min-h-[40px] cursor-pointer items-center">
                    Değişiklik notları ({v.dipnotlar.length})
                  </summary>
                  <ul className="mt-2 space-y-1">
                    {v.dipnotlar.map((d) => (
                      <li key={d.no}>
                        {d.no}. {d.metin}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
              <p className="border-t border-line pt-3 text-xs text-muted">
                Son kontrol: {tarih(v.son_kontrol)}
                {v.url && (
                  <>
                    {" · "}
                    <a
                      href={v.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex min-h-[40px] items-center text-accent underline"
                    >
                      Resmî kaynakta aç
                    </a>
                  </>
                )}
              </p>
            </>
          )}
        </div>
      </aside>
    </div>
  );
}
