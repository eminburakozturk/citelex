"use client";

import Link from "next/link";
import { MotionConfig } from "motion/react";
import { ReactNode, useEffect, useState } from "react";

export type AktifSayfa = "sor" | "degisiklikler" | "pano" | "yontem" | "gelistirici";

const UST_SEKME: { id: AktifSayfa; href: string; ad: string }[] = [
  { id: "sor", href: "/", ad: "Sor" },
  { id: "degisiklikler", href: "/degisiklikler/", ad: "Değişiklikler" },
  { id: "pano", href: "/pano/", ad: "Pano" },
  { id: "yontem", href: "/yontem/", ad: "Yöntem" },
  { id: "gelistirici", href: "/gelistirici/", ad: "Geliştirici" },
];

const MOBIL_ALT_SEKME: { id: Exclude<AktifSayfa, "yontem">; href: string; ad: string }[] = [
  { id: "sor", href: "/", ad: "Sor" },
  { id: "degisiklikler", href: "/degisiklikler/", ad: "Değişiklikler" },
  { id: "pano", href: "/pano/", ad: "Pano" },
  { id: "gelistirici", href: "/gelistirici/", ad: "Geliştirici" },
];

function SekmeIkonu({ id, aktif }: { id: AktifSayfa; aktif: boolean }) {
  const cls = `h-5 w-5 ${aktif ? "stroke-[2.2]" : "stroke-[1.75]"}`;
  if (id === "sor") {
    return (
      <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" className={cls}>
        <circle cx="11" cy="11" r="6.5" />
        <path strokeLinecap="round" d="M16 16l4.5 4.5" />
      </svg>
    );
  }
  if (id === "degisiklikler") {
    return (
      <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" className={cls}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 7v5l3 2" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12a7.5 7.5 0 1 0 2.2-5.3L4.5 9" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 5v4h4" />
      </svg>
    );
  }
  if (id === "pano") {
    return (
      <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" className={cls}>
        <rect x="4" y="13" width="4" height="7" rx="1" />
        <rect x="10" y="9" width="4" height="11" rx="1" />
        <rect x="16" y="5" width="4" height="15" rx="1" />
      </svg>
    );
  }
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" className={cls}>
      <path strokeLinecap="round" strokeLinejoin="round" d="m8 8-4 4 4 4" />
      <path strokeLinecap="round" strokeLinejoin="round" d="m16 8 4 4-4 4" />
      <path strokeLinecap="round" d="m13.5 5.5-3 13" />
    </svg>
  );
}

function TemaDugmesi() {
  const [koyu, setKoyu] = useState(false);
  const [hazir, setHazir] = useState(false);

  useEffect(() => {
    try {
      const kayit = localStorage.getItem("citelex:tema");
      if (kayit === "dark" || kayit === "light") {
        setKoyu(kayit === "dark");
      } else {
        setKoyu(window.matchMedia("(prefers-color-scheme: dark)").matches);
      }
    } catch {
      /* boş */
    }
    setHazir(true);
  }, []);

  function degistir() {
    const yeni = koyu ? "light" : "dark";
    setKoyu(!koyu);
    document.documentElement.setAttribute("data-tema", yeni);
    try {
      localStorage.setItem("citelex:tema", yeni);
    } catch {
      /* boş */
    }
  }

  return (
    <button
      type="button"
      onClick={degistir}
      aria-label={hazir && koyu ? "Açık temaya geç" : "Koyu temaya geç"}
      title={hazir && koyu ? "Açık tema" : "Koyu tema"}
      className="inline-flex min-h-[44px] min-w-[44px] items-center justify-center rounded-full border border-line bg-panel text-muted transition-colors hover:bg-panel-soft hover:text-ink"
    >
      {hazir && koyu ? (
        <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-4 w-4">
          <circle cx="12" cy="12" r="4" />
          <path strokeLinecap="round" d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
        </svg>
      ) : (
        <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-4 w-4">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z"
          />
        </svg>
      )}
    </button>
  );
}

export function SiteKabugu({
  aktif,
  baslikAlt,
  genislik = "dar",
  ustEk,
  children,
}: {
  aktif: AktifSayfa;
  baslikAlt?: string;
  genislik?: "dar" | "genis";
  ustEk?: ReactNode;
  children: ReactNode;
}) {
  const kapGenislik = genislik === "genis" ? "max-w-5xl" : "max-w-3xl";

  return (
    <MotionConfig reducedMotion="user">
      <div className="flex min-h-screen flex-col overflow-x-clip bg-bg text-ink">
        <a
          href="#icerik"
          className="sr-only focus:not-sr-only focus:fixed focus:left-3 focus:top-3 focus:z-50 focus:rounded-lg focus:bg-accent-btn focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-accent-ink"
        >
          İçeriğe geç
        </a>

        <header className="guvenli-ust sticky top-0 z-30 border-b border-line bg-bg/90 backdrop-blur-md">
          <div className={`mx-auto flex ${kapGenislik} items-center justify-between gap-3 px-4 py-2.5`}>
            <div className="flex min-w-0 items-baseline gap-2.5">
              <Link
                href="/"
                prefetch={false}
                className="font-serif text-xl font-semibold tracking-tight text-ink no-underline transition-colors hover:text-accent"
              >
                Citelex
              </Link>
              <span className="hidden truncate text-xs text-subtle sm:inline">
                {baslikAlt ?? "Türk mevzuatı için kaynak gösteren RAG"}
              </span>
            </div>

            <div className="flex items-center gap-2">
              {ustEk}

              <nav aria-label="Ana gezinme" className="hidden items-center gap-1 md:flex">
                {UST_SEKME.map((s) => {
                  const secili = aktif === s.id;
                  return (
                    <Link
                      key={s.id}
                      href={s.href}
                      prefetch={false}
                      aria-current={secili ? "page" : undefined}
                      className={`inline-flex min-h-[40px] items-center rounded-full px-3.5 py-1.5 text-sm transition-colors ${
                        secili
                          ? "bg-accent-btn font-medium text-accent-ink"
                          : "text-muted hover:bg-panel-soft hover:text-ink"
                      }`}
                    >
                      {s.ad}
                    </Link>
                  );
                })}
              </nav>

              <Link
                href="/yontem/"
                prefetch={false}
                aria-current={aktif === "yontem" ? "page" : undefined}
                className={`inline-flex min-h-[44px] items-center rounded-full px-3 py-1.5 text-xs font-medium transition-colors md:hidden ${
                  aktif === "yontem"
                    ? "bg-accent-btn text-accent-ink"
                    : "border border-line bg-panel text-muted hover:text-ink"
                }`}
              >
                Yöntem
              </Link>

              <TemaDugmesi />
            </div>
          </div>
        </header>

        <main id="icerik" className={`mx-auto w-full min-w-0 flex-1 ${kapGenislik} px-4 pt-6 pb-28 md:pt-8 md:pb-12`}>
          {children}
          <p className="mt-10 border-t border-line pt-4 text-center text-xs text-subtle md:hidden">
            Bu sistem hukuki tavsiye vermez. Cevaplar yalnızca gösterilen resmî kaynaklara dayanır.
          </p>
        </main>

        <footer className="hidden border-t border-line bg-bg/70 py-4 text-center text-xs text-subtle md:block">
          <div className={`mx-auto ${kapGenislik} px-4`}>
            Bu sistem hukuki tavsiye vermez. Cevaplar yalnızca gösterilen resmî kaynaklara dayanır.
          </div>
        </footer>

        <nav
          aria-label="Mobil alt gezinme"
          className="guvenli-alt fixed inset-x-0 bottom-0 z-30 border-t border-line bg-panel/95 backdrop-blur-md md:hidden"
        >
          <div className="mx-auto grid max-w-lg grid-cols-4">
            {MOBIL_ALT_SEKME.map((s) => {
              const secili = aktif === s.id;
              return (
                <Link
                  key={s.id}
                  href={s.href}
                  prefetch={false}
                  aria-current={secili ? "page" : undefined}
                  className={`flex min-h-[56px] flex-col items-center justify-center gap-1 px-1 py-1.5 text-[11px] transition-colors ${
                    secili ? "font-semibold text-accent" : "text-muted hover:text-ink"
                  }`}
                >
                  <SekmeIkonu id={s.id} aktif={secili} />
                  <span>{s.ad}</span>
                </Link>
              );
            })}
          </div>
        </nav>
      </div>
    </MotionConfig>
  );
}
