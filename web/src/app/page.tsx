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
  sonuc?: Sonuc;
  hata?: string;
  suruyor: boolean;
}

export default function Sayfa() {
  const [mesajlar, setMesajlar] = useState<Mesaj[]>([]);
  const [girdi, setGirdi] = useState("");
  const [secili, setSecili] = useState<Tur[]>(TURLER.map((t) => t.id));
  const [sonKontrol, setSonKontrol] = useState<string | null>(null);
  const [panel, setPanel] = useState<{ anahtar: string; veri?: KaynakMetni; hata?: string } | null>(null);
  const son = useRef<HTMLDivElement>(null);
  const sayac = useRef(0);
  const mesgul = mesajlar.some((m) => m.suruyor);

  useEffect(() => {
    saglik().then((s) => setSonKontrol(s?.son_kontrol ?? null));
  }, []);
  useEffect(() => {
    son.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [mesajlar]);

  function guncelle(id: number, f: (m: Mesaj) => Mesaj) {
    setMesajlar((ms) => ms.map((m) => (m.id === id ? f(m) : m)));
  }

  async function gonder(soru: string) {
    soru = soru.trim();
    if (soru.length < 3 || mesgul || secili.length === 0) return;
    const id = ++sayac.current;
    setGirdi("");
    setMesajlar((ms) => [...ms, { id, soru, metin: "", baglam: [], suruyor: true }]);
    await sor(soru, secili.length === TURLER.length ? null : secili, {
      baglam: (k) => guncelle(id, (m) => ({ ...m, baglam: k })),
      parca: (t) => guncelle(id, (m) => ({ ...m, metin: m.metin + t })),
      // Doğrulanmış cevap esas alınır: atıf doğrulamasından geçemeyen metin burada "bilmiyorum" ile değişir.
      sonuc: (s) => guncelle(id, (m) => ({ ...m, sonuc: s, metin: s.cevap, suruyor: false })),
      hata: (h) => guncelle(id, (m) => ({ ...m, hata: h, suruyor: false })),
    });
    guncelle(id, (m) => ({ ...m, suruyor: false }));
  }

  async function kaynakAc(anahtar: string) {
    setPanel({ anahtar });
    try {
      const veri = await kaynakGetir(anahtar);
      setPanel((p) => (p?.anahtar === anahtar ? { anahtar, veri } : p));
    } catch (e) {
      setPanel((p) => (p?.anahtar === anahtar ? { anahtar, hata: (e as Error).message } : p));
    }
  }

  return (
    <div className="flex h-full">
      <main className="flex min-w-0 flex-1 flex-col">
        <header className="border-b border-line bg-panel px-4 py-3">
          <div className="mx-auto flex max-w-3xl flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
            <h1 className="text-lg font-semibold tracking-tight">
              Citelex <span className="font-normal text-muted">· kaynak gösteren mevzuat asistanı</span>
            </h1>
            <div className="flex items-baseline gap-3 text-xs text-muted">
              <p>Kaynakların son kontrolü: {tarih(sonKontrol)}</p>
              <Link href="/pano" className="text-accent hover:underline">
                Değerlendirme panosu
              </Link>
              <Link href="/degisiklikler" className="text-accent hover:underline">
                Son değişiklikler
              </Link>
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="mx-auto max-w-3xl space-y-6">
            <p className="rounded-md bg-warn-bg px-3 py-2 text-sm text-warn-ink">
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
                  {ORNEKLER.map((o) => (
                    <button
                      key={o}
                      onClick={() => gonder(o)}
                      className="rounded-md border border-line bg-panel px-3 py-2 text-left text-sm hover:border-accent"
                    >
                      {o}
                    </button>
                  ))}
                </div>
              </section>
            )}

            {mesajlar.map((m) => (
              <article key={m.id} className="space-y-3">
                <p className="ml-auto w-fit max-w-[85%] rounded-lg bg-accent-soft px-3 py-2 text-sm">{m.soru}</p>
                <Cevap m={m} ac={kaynakAc} />
              </article>
            ))}
            <div ref={son} />
          </div>
        </div>

        <footer className="border-t border-line bg-panel px-4 py-3">
          <form
            className="mx-auto max-w-3xl space-y-2"
            onSubmit={(e) => {
              e.preventDefault();
              gonder(girdi);
            }}
          >
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="text-muted">Kaynak türü:</span>
              {TURLER.map((t) => {
                const acik = secili.includes(t.id);
                return (
                  <button
                    key={t.id}
                    type="button"
                    aria-pressed={acik}
                    onClick={() => setSecili((s) => (acik ? s.filter((x) => x !== t.id) : [...s, t.id]))}
                    className={`rounded-full border px-2.5 py-1 ${acik ? "border-accent bg-accent-soft text-ink" : "border-line text-muted"}`}
                  >
                    {t.ad}
                  </button>
                );
              })}
              {secili.length === 0 && <span className="text-accent">En az bir tür seçin.</span>}
            </div>
            <div className="flex gap-2">
              <input
                value={girdi}
                onChange={(e) => setGirdi(e.target.value)}
                maxLength={500}
                placeholder="Sorunuzu yazın…"
                aria-label="Soru"
                className="min-w-0 flex-1 rounded-md border border-line bg-bg px-3 py-2 text-sm outline-none focus:border-accent"
              />
              <button
                type="submit"
                disabled={mesgul || girdi.trim().length < 3 || secili.length === 0}
                className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-bg disabled:opacity-40"
              >
                {mesgul ? "Yanıtlanıyor…" : "Sor"}
              </button>
            </div>
          </form>
        </footer>
      </main>

      {panel && <KaynakPaneli panel={panel} kapat={() => setPanel(null)} />}
    </div>
  );
}

function Cevap({ m, ac }: { m: Mesaj; ac: (anahtar: string) => void }) {
  if (m.hata) return <p className="rounded-md border border-line bg-panel px-3 py-2 text-sm text-accent">{m.hata}</p>;
  const s = m.sonuc;
  // [n] -> kaynak: akış sırasında bağlam listesinden, bitince doğrulanmış kaynak listesinden
  const bul = (n: number) => (s ? s.kaynaklar.find((k) => k.no === n) : m.baglam[n - 1]);
  return (
    <div className="rounded-lg border border-line bg-panel px-4 py-3 text-[15px] leading-relaxed">
      {!m.metin && m.suruyor && <p className="text-sm text-muted">Kaynaklar aranıyor…</p>}
      <p className="whitespace-pre-wrap">
        {m.metin.split(/(\[\d{1,2}\])/).map((parca, i) => {
          const no = /^\[(\d{1,2})\]$/.exec(parca)?.[1];
          const k = no ? bul(Number(no)) : undefined;
          if (!no) return <span key={i}>{parca}</span>;
          if (!k) return null; // doğrulanamayan atıf gösterilmez
          return (
            <button
              key={i}
              onClick={() => ac(k.anahtar)}
              title={k.atif}
              className="mx-0.5 rounded bg-accent-soft px-1.5 align-baseline text-xs font-medium text-accent hover:underline"
            >
              {no}
            </button>
          );
        })}
      </p>
      {s?.bilmiyorum && s.neden && <p className="mt-1 text-sm text-muted">{s.neden}</p>}
      {s && s.kaynaklar.length > 0 && (
        <ul className="mt-3 space-y-1 border-t border-line pt-3 text-sm">
          {s.kaynaklar.map((k) => (
            <li key={k.no} className="flex gap-2">
              <span className="w-5 shrink-0 text-right text-xs font-medium text-accent">{k.no}</span>
              <button onClick={() => ac(k.anahtar)} className="text-left hover:underline">
                {k.atif}
                {k.baslik ? <span className="text-muted"> — {k.baslik}</span> : null}
                <span className="ml-2 text-xs text-muted">{TUR_ADI[k.belge_tur]}</span>
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
  useEffect(() => {
    const f = (e: KeyboardEvent) => e.key === "Escape" && kapat();
    window.addEventListener("keydown", f);
    return () => window.removeEventListener("keydown", f);
  }, [kapat]);
  return (
    <aside
      aria-label="Kaynak metni"
      className="fixed inset-0 z-10 flex flex-col border-l border-line bg-panel md:static md:w-[26rem] md:shrink-0 lg:w-[32rem]"
    >
      <div className="flex items-start justify-between gap-3 border-b border-line px-4 py-3">
        <div className="min-w-0">
          <h2 className="font-semibold">{v?.atif ?? "Kaynak"}</h2>
          {v?.baslik && <p className="text-sm text-muted">{v.baslik}</p>}
        </div>
        <button onClick={kapat} aria-label="Kaynak panelini kapat" className="rounded border border-line px-2 py-1 text-sm">
          Kapat
        </button>
      </div>
      <div className="flex-1 space-y-4 overflow-y-auto px-4 py-4">
        {!v && !panel.hata && <p className="text-sm text-muted">Yükleniyor…</p>}
        {panel.hata && <p className="text-sm text-accent">{panel.hata}</p>}
        {v && (
          <>
            <p className="text-xs text-muted">
              {v.belge_adi}
              {v.karar_tarihi ? ` · ${v.karar_tarihi}` : ""}
            </p>
            {v.mulga && <p className="rounded bg-warn-bg px-2 py-1 text-sm text-warn-ink">Bu hüküm yürürlükten kaldırılmıştır.</p>}
            <div className="kanun-metni space-y-3 text-[15px]">
              {v.parcalar.map((p, i) => (
                <div key={i} className={p.mulga ? "opacity-50" : ""}>
                  {p.bolum && (i === 0 || v.parcalar[i - 1].bolum !== p.bolum) && (
                    <h3 className="mb-1 font-sans text-xs font-semibold uppercase tracking-wide text-muted">
                      {BOLUM_ADI[p.bolum] ?? p.bolum}
                    </h3>
                  )}
                  <p className="whitespace-pre-wrap">{p.metin}</p>
                </div>
              ))}
            </div>
            {v.dipnotlar.length > 0 && (
              <details className="text-sm text-muted">
                <summary className="cursor-pointer">Değişiklik notları ({v.dipnotlar.length})</summary>
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
                  <a href={v.url} target="_blank" rel="noopener noreferrer" className="text-accent underline">
                    Resmî kaynakta aç
                  </a>
                </>
              )}
            </p>
          </>
        )}
      </div>
    </aside>
  );
}
