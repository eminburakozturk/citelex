"use client";

import { useEffect, useRef, useState } from "react";
import {
  IliskiliMadde,
  KaynakMetni,
  KaynakParcasi,
  SadeAciklama,
  aciklamaGetir,
  kisaAtif,
  tarih,
} from "@/lib/api";

type Sekme = "metin" | "sade" | "gecmis" | "iliskili";

const TUR_AD: Record<string, string> = {
  kanun: "Kanun",
  yonetmelik: "Yönetmelik",
  teblig: "Tebliğ",
  karar: "Kurul kararı",
};

function AlintiVurguluMetin({ metin, alinti }: { metin?: string | null; alinti?: string }) {
  const guvenliMetin = typeof metin === "string" ? metin : "";
  if (!guvenliMetin || !alinti) return <>{guvenliMetin}</>;
  const kisa = alinti.replace(/^\.\.\.|\.\.\.$/g, "").trim();
  if (kisa.length < 24) return <>{guvenliMetin}</>;
  const parca = kisa.slice(0, 60);
  const idx = guvenliMetin.indexOf(parca);
  if (idx === -1) return <>{guvenliMetin}</>;
  const bitis = Math.min(guvenliMetin.length, idx + Math.min(kisa.length, 220));
  return (
    <>
      {guvenliMetin.slice(0, idx)}
      <mark className="rounded bg-accent-soft px-0.5 text-ink">{guvenliMetin.slice(idx, bitis)}</mark>
      {guvenliMetin.slice(bitis)}
    </>
  );
}

function IliskiliAgiSvg({
  merkezAtif,
  merkezAnahtar,
  merkezBaslik,
  baglantilar,
  onSec,
}: {
  merkezAtif: string;
  merkezAnahtar?: string;
  merkezBaslik?: string | null;
  baglantilar: IliskiliMadde[];
  onSec: (anahtar: string, atif?: string) => void;
}) {
  const gosterilen = baglantilar.slice(0, 6);
  const W = 460;
  const H = 240;
  const cx = W / 2;
  const cy = H / 2;
  const rx = 152;
  const ry = 80;
  const merkezKisa = kisaAtif(merkezAtif, merkezAnahtar);
  const merkezTam = `${merkezAtif}${merkezBaslik ? ` — ${merkezBaslik}` : ""}`;

  return (
    <div className="rounded-xl border border-line bg-bg/70 p-3">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2 text-[11px] text-muted">
        <span className="font-medium text-ink">Madde bağlantı ağı</span>
        <span className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-accent" /> Atıf yapar
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-info" /> Atıf alır
          </span>
        </span>
      </div>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-label={`${merkezAtif} ile ilişkili ${gosterilen.length} madde bağlantı şeması`}
        className="block h-auto w-full max-w-full select-none"
      >
        {gosterilen.map((item, i) => {
          const aci = (i / Math.max(gosterilen.length, 1)) * Math.PI * 2 - Math.PI / 2;
          const x = cx + Math.cos(aci) * rx;
          const y = cy + Math.sin(aci) * ry;
          const renk = item.iliski === "atif_yapar" ? "var(--accent)" : "var(--info)";
          const etiket = kisaAtif(item.atif, item.anahtar);
          const tamBaslik = (item.baslik ?? "").trim();
          const kisaBaslik = tamBaslik.length > 20 ? `${tamBaslik.slice(0, 19)}…` : tamBaslik;
          const tamAciklama = `${item.atif || etiket}${tamBaslik ? ` — ${tamBaslik}` : ""}`;

          return (
            <g key={item.anahtar}>
              <line
                x1={cx}
                y1={cy}
                x2={x}
                y2={y}
                stroke={renk}
                strokeOpacity="0.45"
                strokeWidth="1.5"
                strokeDasharray={item.iliski === "atif_alir" ? "4 3" : undefined}
              />
              <g
                role="button"
                tabIndex={0}
                aria-label={`${tamAciklama} maddesini incele`}
                onClick={() => onSec(item.anahtar, item.atif || etiket)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    onSec(item.anahtar, item.atif || etiket);
                  }
                }}
                className="cursor-pointer"
              >
                <title>{tamAciklama}</title>
                <rect
                  x={x - 68}
                  y={y - 20}
                  width={136}
                  height={40}
                  rx={8}
                  fill="var(--panel)"
                  stroke={renk}
                  strokeWidth="1.2"
                />
                <text
                  x={x}
                  y={kisaBaslik ? y - 3 : y + 4}
                  textAnchor="middle"
                  fontSize="10.5"
                  fontWeight="600"
                  fill="var(--ink)"
                >
                  {etiket}
                </text>
                {kisaBaslik && (
                  <text
                    x={x}
                    y={y + 11}
                    textAnchor="middle"
                    fontSize="8.8"
                    fill="var(--muted)"
                  >
                    {kisaBaslik}
                  </text>
                )}
              </g>
            </g>
          );
        })}

        <g>
          <title>{merkezTam}</title>
          <rect
            x={cx - 68}
            y={cy - 19}
            width={136}
            height={38}
            rx={10}
            fill="var(--accent-btn)"
          />
          <text
            x={cx}
            y={merkezBaslik ? cy - 2 : cy + 4}
            textAnchor="middle"
            fontSize="11"
            fontWeight="600"
            fill="var(--accent-ink)"
          >
            {merkezKisa}
          </text>
          {merkezBaslik && (
            <text
              x={cx}
              y={cy + 11}
              textAnchor="middle"
              fontSize="8.8"
              fill="var(--accent-ink)"
              fillOpacity="0.88"
            >
              {merkezBaslik.length > 20 ? `${merkezBaslik.slice(0, 19)}…` : merkezBaslik}
            </text>
          )}
        </g>
      </svg>
    </div>
  );
}

export function KaynakPaneli({
  secili,
  veri,
  yukleniyor,
  hata,
  oncekiKaynak,
  onGeriDon,
  onKapat,
  onAnahtarSec,
}: {
  secili: { anahtar: string; atif: string; alinti?: string };
  veri: KaynakMetni | null;
  yukleniyor: boolean;
  hata: string | null;
  oncekiKaynak?: { anahtar: string; atif: string } | null;
  onGeriDon?: () => void;
  onKapat: () => void;
  onAnahtarSec: (anahtar: string, atif?: string) => void;
}) {
  const panelRef = useRef<HTMLDivElement>(null);
  const [sekme, setSekme] = useState<Sekme>("metin");
  const [aciklama, setAciklama] = useState<SadeAciklama | null>(null);
  const [aciklamaYukleniyor, setAciklamaYukleniyor] = useState(false);
  const [aciklamaHata, setAciklamaHata] = useState<string | null>(null);

  useEffect(() => {
    panelRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onKapat();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onKapat]);

  useEffect(() => {
    setSekme("metin");
    setAciklama(null);
    setAciklamaHata(null);
    setAciklamaYukleniyor(false);
  }, [secili.anahtar]);

  async function sadeAciklamaYukle() {
    if (aciklamaYukleniyor) return;
    setAciklamaYukleniyor(true);
    setAciklamaHata(null);
    try {
      const yanit = await aciklamaGetir(secili.anahtar);
      setAciklama(yanit);
    } catch (e) {
      setAciklamaHata((e as Error).message || "Sade açıklama alınamadı.");
    } finally {
      setAciklamaYukleniyor(false);
    }
  }

  const parcalar: KaynakParcasi[] = veri?.parcalar?.length
    ? veri.parcalar
    : veri?.metin
      ? [{ metin: veri.metin }]
      : [];

  const gecmisVar = Boolean(veri?.gecmis && veri.gecmis.length > 0);
  const iliskiliVar = Boolean(veri?.iliskili && veri.iliskili.length > 0);

  const sekmeler: { id: Sekme; ad: string }[] = [
    { id: "metin", ad: "Metin" },
    { id: "sade", ad: "Sade açıklama" },
    ...(gecmisVar ? [{ id: "gecmis" as const, ad: `Geçmiş (${veri!.gecmis!.length})` }] : []),
    ...(iliskiliVar ? [{ id: "iliskili" as const, ad: `İlişkili (${veri!.iliskili!.length})` }] : []),
  ];

  const turEtiketi = veri?.belge_tur ? (TUR_AD[veri.belge_tur] ?? veri.belge_tur) : null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-end bg-black/45 backdrop-blur-[1px] sm:items-stretch"
      role="dialog"
      aria-modal="true"
      aria-labelledby="kaynak-baslik"
      onClick={(e) => {
        if (e.target === e.currentTarget) onKapat();
      }}
    >
      <div
        ref={panelRef}
        tabIndex={-1}
        className="flex max-h-[88dvh] w-full flex-col rounded-t-2xl border-t border-line bg-panel shadow-2xl outline-none sm:max-h-none sm:max-w-xl sm:rounded-none sm:border-t-0 sm:border-l"
      >
        <div className="flex items-start justify-between gap-3 border-b border-line px-5 py-4">
          <div className="min-w-0 space-y-1">
            {oncekiKaynak && onGeriDon && (
              <div className="pb-1">
                <button
                  type="button"
                  onClick={onGeriDon}
                  className="inline-flex min-h-[34px] items-center gap-1.5 rounded-lg border border-line bg-bg px-2.5 py-1 text-xs font-medium text-accent transition-colors hover:border-accent hover:bg-accent-soft"
                >
                  <span aria-hidden="true">←</span>
                  <span>
                    Önceki maddeye dön ({kisaAtif(oncekiKaynak.atif, oncekiKaynak.anahtar)})
                  </span>
                </button>
              </div>
            )}
            <div className="flex flex-wrap items-center gap-2">
              {turEtiketi && (
                <span className="rounded-full bg-accent-soft px-2.5 py-0.5 text-[11px] font-semibold text-accent">
                  {turEtiketi}
                </span>
              )}
              {veri?.mulga && (
                <span className="rounded-full bg-warn-bg px-2.5 py-0.5 text-[11px] font-semibold text-warn-ink">
                  Mülga
                </span>
              )}
              {veri?.diger_kanuna_islendi && (
                <span className="rounded-full bg-warn-bg px-2.5 py-0.5 text-[11px] font-semibold text-warn-ink">
                  Başka kanuna işlendi
                </span>
              )}
              {veri && !veri.mulga && !veri.diger_kanuna_islendi && (
                <span className="rounded-full bg-ok-bg px-2.5 py-0.5 text-[11px] font-semibold text-ok">
                  Yürürlükte
                </span>
              )}
            </div>
            <h2 id="kaynak-baslik" className="font-serif text-lg font-medium text-ink">
              {veri?.atif ?? secili.atif}
            </h2>
            {veri?.belge_adi && <p className="text-xs text-muted">{veri.belge_adi}</p>}
            {veri?.baslik && <p className="font-serif text-sm italic text-muted">{veri.baslik}</p>}
          </div>

          <button
            type="button"
            onClick={onKapat}
            aria-label="Kaynak panelini kapat"
            className="inline-flex min-h-[44px] min-w-[44px] shrink-0 items-center justify-center rounded-full border border-line bg-bg text-muted transition-colors hover:border-accent hover:text-ink"
          >
            <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-4 w-4">
              <path strokeLinecap="round" d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </div>

        <div className="border-b border-line bg-bg/60 px-5 py-2">
          <div role="tablist" aria-label="Kaynak inceleme sekmeleri" className="flex flex-wrap gap-1">
            {sekmeler.map((s) => {
              const aktif = sekme === s.id;
              return (
                <button
                  key={s.id}
                  type="button"
                  role="tab"
                  aria-selected={aktif}
                  onClick={() => setSekme(s.id)}
                  className={`min-h-[38px] rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                    aktif
                      ? "bg-panel text-ink shadow-xs ring-1 ring-line"
                      : "text-muted hover:text-ink"
                  }`}
                >
                  {s.ad}
                </button>
              );
            })}
          </div>
        </div>

        <div className="guvenli-alt flex-1 overflow-y-auto px-5 py-4 text-sm">
          {yukleniyor && (
            <div className="space-y-3 py-4" role="status">
              <div className="h-4 w-3/4 animate-pulse rounded bg-panel-soft" />
              <div className="h-4 w-full animate-pulse rounded bg-panel-soft" />
              <div className="h-4 w-5/6 animate-pulse rounded bg-panel-soft" />
            </div>
          )}

          {hata && (
            <p role="alert" className="rounded-lg border border-warn-border bg-warn-bg px-3 py-2 text-xs text-warn-ink">
              {hata}
            </p>
          )}

          {!yukleniyor && !hata && veri && sekme === "metin" && (
            <div className="space-y-4">
              {parcalar.length === 0 ? (
                <p className="text-xs text-muted">Bu kaynak için görüntülenecek metin bulunamadı.</p>
              ) : (
                <div className="space-y-4">
                  {parcalar.map((p, idx) => (
                    <div key={idx} className="space-y-1">
                      {(p.fikra_no != null || p.bolum) && (
                        <div className="text-xs font-semibold text-accent">
                          {p.fikra_no != null ? `(${p.fikra_no})` : p.bolum}
                        </div>
                      )}
                      <div className="kanun-metni whitespace-pre-wrap text-ink">
                        <AlintiVurguluMetin metin={p.metin} alinti={secili.alinti} />
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {veri.dipnotlar?.length > 0 && (
                <details className="rounded-xl border border-line bg-bg/50 p-3 text-xs">
                  <summary className="flex min-h-[40px] cursor-pointer items-center font-medium text-muted hover:text-ink">
                    Değişiklik dipnotları ({veri.dipnotlar.length})
                  </summary>
                  <ul className="mt-2 space-y-1.5 border-t border-line pt-2 text-muted">
                    {veri.dipnotlar.map((d, i) => (
                      <li key={i} className="leading-relaxed">
                        {d.no != null && d.no !== "" ? <span className="font-semibold text-ink">({d.no}) </span> : null}
                        {d.metin}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          )}

          {!yukleniyor && !hata && sekme === "sade" && (
            <div className="space-y-4">
              {!aciklama && !aciklamaYukleniyor && (
                <div className="space-y-3 rounded-xl border border-line bg-bg/60 p-4">
                  <p className="text-xs leading-relaxed text-muted">
                    Bu maddenin yalnızca kendi resmî metnine dayanarak maddeler hâlinde sade açıklaması
                    oluşturulur.
                  </p>
                  <button
                    type="button"
                    onClick={sadeAciklamaYukle}
                    className="inline-flex min-h-[44px] items-center justify-center rounded-lg bg-accent-btn px-4 py-2 text-xs font-medium text-accent-ink transition-colors hover:bg-accent-btn-hover"
                  >
                    Sade açıklama oluştur
                  </button>
                </div>
              )}

              {aciklamaYukleniyor && (
                <div role="status" className="rounded-xl border border-line bg-bg/60 p-4 text-xs text-muted">
                  Sade açıklama hazırlanıyor…
                </div>
              )}

              {aciklamaHata && (
                <div role="alert" className="space-y-2 rounded-xl border border-warn-border bg-warn-bg p-3 text-xs text-warn-ink">
                  <p>{aciklamaHata}</p>
                  <button
                    type="button"
                    onClick={sadeAciklamaYukle}
                    className="font-medium underline"
                  >
                    Tekrar dene
                  </button>
                </div>
              )}

              {aciklama && (
                <div className="space-y-4">
                  <div className="inline-flex items-center gap-1.5 rounded-full bg-info-bg px-3 py-1 text-[11px] font-medium text-info">
                    Yapay zekâ açıklaması · yalnızca bu maddeye dayanır
                  </div>

                  <ul className="space-y-2 rounded-xl border border-line bg-bg/50 p-4 text-sm leading-relaxed text-ink">
                    {aciklama.maddeler.map((m, idx) => (
                      <li key={idx} className="flex gap-2.5">
                        <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
                        <span>{m}</span>
                      </li>
                    ))}
                  </ul>

                  {aciklama.ornek && (
                    <div className="rounded-xl border border-line bg-panel-soft/60 p-3.5 text-xs leading-relaxed text-ink">
                      <div className="mb-1 font-semibold text-accent">Örnek</div>
                      <p>{aciklama.ornek}</p>
                    </div>
                  )}

                  {aciklama.uyari && (
                    <p role="note" className="rounded-lg bg-warn-bg px-3 py-2 text-xs text-warn-ink">
                      {aciklama.uyari}
                    </p>
                  )}
                </div>
              )}
            </div>
          )}

          {!yukleniyor && !hata && veri && sekme === "gecmis" && gecmisVar && (
            <ol className="relative space-y-4 border-l-2 border-line pl-4">
              {veri.gecmis!.map((g, i) => (
                <li key={`${g.tarih}-${i}`} className="relative space-y-1">
                  <span
                    aria-hidden="true"
                    className="absolute -left-[21px] top-1.5 h-2.5 w-2.5 rounded-full border-2 border-panel bg-accent"
                  />
                  <div className="flex flex-wrap items-center gap-2 text-xs">
                    <span className="font-semibold tabular-nums text-accent">{tarih(g.tarih)}</span>
                    {g.kanun && (
                      <span className="rounded bg-panel-soft px-2 py-0.5 font-medium text-ink">{g.kanun}</span>
                    )}
                  </div>
                  <p className="text-xs leading-relaxed text-muted">{g.aciklama}</p>
                </li>
              ))}
            </ol>
          )}

          {!yukleniyor && !hata && veri && sekme === "iliskili" && iliskiliVar && (
            <div className="space-y-4">
              <IliskiliAgiSvg
                merkezAtif={veri.atif}
                merkezAnahtar={veri.anahtar}
                merkezBaslik={veri.baslik}
                baglantilar={veri.iliskili!}
                onSec={onAnahtarSec}
              />

              <ul className="space-y-2">
                {veri.iliskili!.map((il) => {
                  const kisa = kisaAtif(il.atif, il.anahtar);
                  const tamAtif = il.atif || kisa;
                  const tamAciklama = `${tamAtif}${il.baslik ? ` — ${il.baslik}` : ""}`;
                  return (
                    <li key={il.anahtar}>
                      <button
                        type="button"
                        title={tamAciklama}
                        onClick={() => onAnahtarSec(il.anahtar, tamAtif)}
                        className="flex w-full items-center justify-between gap-3 rounded-xl border border-line bg-bg/60 px-3.5 py-2.5 text-left transition-colors hover:border-accent hover:bg-panel-soft/60"
                      >
                        <div className="min-w-0 space-y-0.5">
                          <div className="flex flex-wrap items-center gap-2">
                            <span
                              className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                                il.iliski === "atif_yapar"
                                  ? "bg-accent-soft text-accent"
                                  : "bg-info-bg text-info"
                              }`}
                            >
                              {il.iliski === "atif_yapar" ? "Atıf yapar" : "Atıf alır"}
                            </span>
                            <span
                              title={tamAtif}
                              className="shrink-0 font-mono text-xs font-semibold text-ink"
                            >
                              {kisa}
                            </span>
                            {il.atif && il.atif !== kisa && (
                              <span
                                title={il.atif}
                                className="truncate text-[11px] text-muted"
                              >
                                ({il.atif})
                              </span>
                            )}
                          </div>
                          {il.baslik && (
                            <p
                              title={il.baslik}
                              className="truncate font-serif text-xs text-muted"
                            >
                              {il.baslik}
                            </p>
                          )}
                        </div>
                        <span className="shrink-0 text-xs font-medium text-accent">İncele →</span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          )}
        </div>

        {veri && (
          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line bg-bg/60 px-5 py-3 text-xs text-muted">
            <span>{veri.son_kontrol ? `Son kontrol: ${tarih(veri.son_kontrol)}` : "Resmî derlem"}</span>
            {veri.url && (
              <a
                href={veri.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex min-h-[40px] items-center font-medium text-accent underline underline-offset-4 hover:text-accent-hover"
              >
                Resmî metne git ↗
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
