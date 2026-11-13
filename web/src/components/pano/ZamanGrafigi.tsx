"use client";

import { useState } from "react";
import { GecmisKaydi, tarihSaat, yapilandirmaEtiketi, yuzde } from "./types";

const RENKLER = ["var(--accent)", "#4b83b8", "#3d9468", "#c27d28", "#8f6cb8", "#b35c7e"];

export function ZamanGrafigi({ gecmis }: { gecmis: GecmisKaydi[] }) {
  const [seciliIdx, setSeciliIdx] = useState<number | null>(null);

  const gecerli = gecmis.filter((g) => g.dogru_orani != null && g.tam);
  if (gecerli.length === 0) {
    return null;
  }

  const seriler = Array.from(new Set(gecerli.map((g) => g.anahtar)));
  const etiketMap = Object.fromEntries(
    gecerli.map((g) => [g.anahtar, yapilandirmaEtiketi(g.llm, g.yapilandirma, g.yapilandirma_adi)])
  );
  const renkMap = Object.fromEntries(seriler.map((a, i) => [a, RENKLER[i % RENKLER.length]]));

  const oranlar = gecerli.map((g) => (g.dogru_orani ?? 0) * 100);
  const minVal = Math.max(0, Math.floor((Math.min(...oranlar) - 8) / 10) * 10);
  const maxVal = Math.min(100, Math.ceil((Math.max(...oranlar) + 5) / 10) * 10);
  const span = Math.max(10, maxVal - minVal);

  const W = 720;
  const H = 240;
  const PAD_L = 52;
  const PAD_R = 40;
  const INSET = 32;
  const PAD_T = 22;
  const PAD_B = 46;
  const plotW = W - PAD_L - PAD_R - INSET * 2;
  const plotH = H - PAD_T - PAD_B;

  const xPos = (idx: number) =>
    gecerli.length === 1 ? PAD_L + INSET + plotW / 2 : PAD_L + INSET + (idx / (gecerli.length - 1)) * plotW;
  const yPos = (pct: number) => PAD_T + ((maxVal - pct) / span) * plotH;

  const yTicks: number[] = [];
  for (let v = minVal; v <= maxVal; v += 10) yTicks.push(v);

  const noktalar = gecerli.map((g, idx) => ({
    idx,
    kayit: g,
    x: xPos(idx),
    y: yPos((g.dogru_orani ?? 0) * 100),
    renk: renkMap[g.anahtar],
  }));

  const aktif = seciliIdx != null ? noktalar[seciliIdx] : noktalar[noktalar.length - 1];

  return (
    <section aria-labelledby="zaman-grafik-baslik" className="space-y-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 id="zaman-grafik-baslik" className="text-base font-semibold">
          Doğruluğun zaman içindeki değişimi
        </h2>
        <p className="text-xs text-muted">{gecerli.length} tam çalıştırma (eval_history.jsonl)</p>
      </div>

      <div className="rounded-lg border border-line bg-panel p-4">
        <div className="mb-3 flex flex-wrap gap-x-4 gap-y-1.5 text-xs">
          {seriler.map((a) => (
            <span key={a} className="inline-flex items-center gap-1.5 text-ink">
              <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: renkMap[a] }} />
              {etiketMap[a]}
            </span>
          ))}
        </div>

        <svg
          viewBox={`0 0 ${W} ${H}`}
          role="img"
          aria-label="Modellerin zaman içindeki doğruluk oranı çizgi grafiği"
          className="h-auto w-full overflow-visible"
        >
          {yTicks.map((v) => {
            const y = yPos(v);
            return (
              <g key={v}>
                <line x1={PAD_L} y1={y} x2={W - PAD_R} y2={y} stroke="var(--line)" strokeDasharray="3 3" />
                <text x={PAD_L - 8} y={y + 4} textAnchor="end" fontSize="11" fill="var(--muted)">
                  %{v}
                </text>
              </g>
            );
          })}

          <line x1={PAD_L} y1={PAD_T} x2={PAD_L} y2={H - PAD_B} stroke="var(--line)" />
          <line x1={PAD_L} y1={H - PAD_B} x2={W - PAD_R} y2={H - PAD_B} stroke="var(--line)" />

          {seriler.map((a) => {
            const pts = noktalar.filter((n) => n.kayit.anahtar === a);
            if (pts.length < 2) return null;
            return (
              <polyline
                key={a}
                fill="none"
                stroke={renkMap[a]}
                strokeWidth="2"
                strokeLinejoin="round"
                points={pts.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ")}
              />
            );
          })}

          {noktalar.map((n) => {
            const secili = aktif?.idx === n.idx;
            return (
              <g key={`${n.kayit.tarih}-${n.kayit.anahtar}-${n.idx}`}>
                <text x={n.x} y={H - PAD_B + 16} textAnchor="middle" fontSize="9.5" fill="var(--muted)">
                  {tarihSaat(n.kayit.tarih)}
                </text>
                <circle
                  cx={n.x}
                  cy={n.y}
                  r={secili ? 6 : 4.5}
                  fill={n.renk}
                  stroke="var(--panel)"
                  strokeWidth="1.5"
                  className="cursor-pointer"
                  onMouseEnter={() => setSeciliIdx(n.idx)}
                  onClick={() => setSeciliIdx(n.idx)}
                />
                <text
                  x={n.x}
                  y={n.y - 9}
                  textAnchor="middle"
                  fontSize="10"
                  fontWeight={secili ? "600" : "400"}
                  fill="var(--ink)"
                >
                  {yuzde(n.kayit.dogru_orani)}
                </text>
              </g>
            );
          })}
        </svg>

        {aktif && (
          <div className="mt-2 flex flex-wrap items-center justify-between gap-2 border-t border-line pt-2.5 text-xs text-muted">
            <span>
              <strong className="text-ink">
                {yapilandirmaEtiketi(aktif.kayit.llm, aktif.kayit.yapilandirma, aktif.kayit.yapilandirma_adi)}
              </strong>{" "}
              · {tarihSaat(aktif.kayit.tarih)} · <code>{aktif.kayit.commit}</code>
            </span>
            <span className="tabular-nums">
              Doğru {aktif.kayit.dogru}/{aktif.kayit.n_ic} ({yuzde(aktif.kayit.dogru_orani)}) · bağlam{" "}
              {aktif.kayit.baglam}/{aktif.kayit.n_ic} · yanlış ret {aktif.kayit.yanlis_ret} · kapsam dışı ret{" "}
              {aktif.kayit.dogru_ret}/{aktif.kayit.n_dis}
            </span>
          </div>
        )}
      </div>
    </section>
  );
}
