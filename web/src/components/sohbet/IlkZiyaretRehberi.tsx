"use client";

import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";

const DEPO_ANAHTARI = "citelex:rehber_gizle";

export function IlkZiyaretRehberi() {
  const [acik, setAcik] = useState(false);

  useEffect(() => {
    try {
      if (localStorage.getItem(DEPO_ANAHTARI) !== "1") {
        setAcik(true);
      }
    } catch {
      setAcik(true);
    }
  }, []);

  function kapat() {
    setAcik(false);
    try {
      localStorage.setItem(DEPO_ANAHTARI, "1");
    } catch {
      /* boş */
    }
  }

  return (
    <AnimatePresence>
      {acik && (
        <motion.aside
          aria-label="İlk ziyaret rehberi"
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
          transition={{ duration: 0.2 }}
          className="rounded-xl border border-line bg-panel p-4 shadow-xs"
        >
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="space-y-1">
              <div className="text-xs font-semibold tracking-wide text-accent uppercase">
                Nasıl çalışır?
              </div>
              <p className="text-sm leading-relaxed text-muted">
                Her cümlede yalnız getirilen mevzuata ve Kurul kararlarına dayanan numaralı{" "}
                <span className="font-semibold text-ink">[n]</span> atıfları üretilir; kanıt yoksa sistem
                &ldquo;bilmiyorum&rdquo; der.
              </p>
            </div>
            <button
              type="button"
              onClick={kapat}
              className="inline-flex min-h-[44px] shrink-0 items-center justify-center rounded-lg border border-line bg-panel-soft px-4 py-2 text-xs font-medium text-ink transition-colors hover:border-accent hover:text-accent"
            >
              Anladım
            </button>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
