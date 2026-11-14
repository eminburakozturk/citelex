"use client";

import { AnimatePresence, motion } from "motion/react";
import { useEffect, useRef, useState } from "react";
import { Adim, AdimAdi, AdimDurumu, Sonuc } from "@/lib/api";

const ADIM_ADLARI: Record<AdimAdi, string> = {
  arama: "Mevzuat ve karar araması",
  esik: "Güven eşiği kontrolü",
  yeniden_yazma: "Sorguyu yeniden yazma",
  llm: "Kaynaklı cevap üretimi",
  atif_dogrulama: "Cümle ve atıf doğrulama",
};

const DURUM_ETIKET: Record<AdimDurumu, { yazi: string; sinif: string }> = {
  tamam: { yazi: "Tamam", sinif: "bg-ok-bg text-ok" },
  atlandi: { yazi: "Atlandı", sinif: "bg-panel-soft text-muted" },
  basarisiz: { yazi: "Eşik altı", sinif: "bg-warn-bg text-warn-ink" },
};

function AdimSatiri({ adim, index }: { adim: Adim; index: number }) {
  const d = DURUM_ETIKET[adim.durum] ?? { yazi: adim.durum, sinif: "bg-panel-soft text-muted" };
  return (
    <motion.li
      initial={{ opacity: 0, x: -4 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.16, delay: Math.min(index * 0.06, 0.3) }}
      className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-line bg-bg/60 px-3 py-2 text-xs"
    >
      <div className="flex min-w-0 items-center gap-2">
        <span className={`rounded px-1.5 py-0.5 text-[11px] font-medium ${d.sinif}`}>{d.yazi}</span>
        <span className="font-medium text-ink">{ADIM_ADLARI[adim.ad] ?? adim.ad}</span>
        {adim.detay && <span className="truncate text-muted">· {adim.detay}</span>}
      </div>
      {Number.isFinite(adim.sure_sn) && (
        <span className="shrink-0 tabular-nums text-subtle">{adim.sure_sn.toFixed(2)} sn</span>
      )}
    </motion.li>
  );
}

export function SurecZamanCizgisi({
  yukleniyor,
  ajan,
  uzunBekleme,
  akisBasladi,
  sonuc,
}: {
  yukleniyor: boolean;
  ajan: boolean;
  uzunBekleme: boolean;
  akisBasladi: boolean;
  sonuc: Sonuc | null;
}) {
  const [acik, setAcik] = useState(true);
  const kullaniciSecimiRef = useRef(false);

  useEffect(() => {
    kullaniciSecimiRef.current = false;
    setAcik(true);
  }, [yukleniyor]);

  useEffect(() => {
    if (!sonuc?.adimlar?.length) return;
    const t = setTimeout(() => {
      if (!kullaniciSecimiRef.current) {
        setAcik(false);
      }
    }, 2400);
    return () => clearTimeout(t);
  }, [sonuc]);

  if (yukleniyor && !akisBasladi) {
    return (
      <div
        role="status"
        className="flex items-center gap-3 rounded-xl border border-line bg-panel px-4 py-3 text-sm text-muted"
      >
        <span className="relative flex h-2.5 w-2.5 shrink-0">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-60" />
          <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-accent" />
        </span>
        <span>
          {ajan && uzunBekleme
            ? "Arama ve doğrulama sürüyor (derin arama etkin)…"
            : "Kaynaklar aranıyor…"}
        </span>
      </div>
    );
  }

  if (!sonuc) return null;

  const adimlar = sonuc.adimlar ?? [];
  const yenidenSorguNotu =
    sonuc.ajan_deneme === 2 && sonuc.ajan_sorgular && sonuc.ajan_sorgular.length > 1
      ? sonuc.ajan_sorgular[1]
      : null;

  if (adimlar.length === 0) {
    if (!yenidenSorguNotu) return null;
    return (
      <p role="note" className="rounded-xl border border-line bg-panel px-4 py-2.5 text-xs text-muted">
        İlk arama eşik altında kaldığı için sorgu{" "}
        <strong className="font-medium text-ink">&ldquo;{yenidenSorguNotu}&rdquo;</strong> olarak yeniden
        arandı.
      </p>
    );
  }

  return (
    <div className="rounded-xl border border-line bg-panel px-3.5 py-2.5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <button
          type="button"
          aria-expanded={acik}
          onClick={() => {
            kullaniciSecimiRef.current = true;
            setAcik((v) => !v);
          }}
          className="inline-flex min-h-[40px] items-center gap-2 text-xs font-medium text-ink transition-colors hover:text-accent"
        >
          <span className="inline-flex h-5 items-center rounded-full bg-ok-bg px-2 text-[11px] font-semibold text-ok">
            {adimlar.length} adım
          </span>
          {sonuc.sure_sn != null && (
            <span className="tabular-nums text-muted">Toplam {sonuc.sure_sn.toFixed(2)} sn</span>
          )}
          <span className="text-subtle">· {acik ? "Gizle" : "Süreci göster"}</span>
        </button>

        {yenidenSorguNotu && (
          <span className="rounded-full bg-accent-soft px-2.5 py-1 text-[11px] font-medium text-accent">
            2. deneme: &ldquo;{yenidenSorguNotu}&rdquo;
          </span>
        )}
      </div>

      <AnimatePresence initial={false}>
        {acik && (
          <motion.ol
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="mt-2.5 space-y-1.5 overflow-hidden border-t border-line pt-2.5"
          >
            {adimlar.map((a, idx) => (
              <AdimSatiri key={`${a.ad}-${idx}`} adim={a} index={idx} />
            ))}
          </motion.ol>
        )}
      </AnimatePresence>
    </div>
  );
}
