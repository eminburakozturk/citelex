// Citelex API istemcisi: /sor (SSE akışı), /kaynak, /saglik.

// "same-origin": arayüz API ile aynı adresten sunuluyor (yayın). Aksi halde tam adres (geliştirme, Tauri).
const HAM = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
export const API_URL = HAM === "same-origin" ? "" : HAM.replace(/\/$/, "");

export type Tur = "kanun" | "yonetmelik" | "teblig" | "karar";

export interface Kaynak {
  no: number;
  atif: string;
  anahtar: string;
  belge_tur: Tur;
  baslik?: string | null;
  url?: string | null;
  alinti: string;
}

export interface Sonuc {
  bilmiyorum: boolean;
  cevap: string;
  neden?: string;
  kaynaklar: Kaynak[];
  kanallar?: string[];
  uyari: string;
  son_kontrol?: string | null;
  sure_sn?: number;
  llm?: string;
  ajan_deneme?: number;
  ajan_sorgular?: string[];
}

export interface KaynakMetni {
  anahtar: string;
  atif: string;
  belge_tur: Tur;
  belge_adi: string;
  baslik?: string | null;
  url?: string | null;
  karar_tarihi?: string | null;
  mulga: boolean;
  son_kontrol?: string | null;
  parcalar: { fikra_no: number | null; bolum: string | null; metin: string; mulga: boolean }[];
  dipnotlar: { no: number; metin: string }[];
}

export interface Olaylar {
  baglam: (kaynaklar: Kaynak[]) => void;
  parca: (metin: string) => void;
  sonuc: (s: Sonuc) => void;
  hata: (mesaj: string) => void;
}

const BAGLANTI_HATASI = "Sunucuya ulaşılamadı. Bağlantınızı kontrol edip tekrar deneyin.";

/** Soruyu gönderir ve SSE olaylarını sırayla işler. Akış bitince döner. */
export async function sor(
  soru: string,
  turler: Tur[] | null,
  on: Olaylar,
  signal?: AbortSignal,
  ajan = true
): Promise<void> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}/sor`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ soru, ...(turler ? { turler } : {}), ajan }),
      signal,
    });
  } catch {
    on.hata(BAGLANTI_HATASI);
    return;
  }
  if (!res.ok || !res.body) {
    let mesaj = "Bir hata oluştu. Lütfen tekrar deneyin.";
    try {
      const j = await res.json();
      if (typeof j.detail === "string") mesaj = j.detail;
      else if (res.status === 422) mesaj = "Soru 3 ile 500 karakter arasında olmalı.";
    } catch {}
    on.hata(mesaj);
    return;
  }
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = "";
  let bitti = false;
  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      let i: number;
      while ((i = buf.indexOf("\n\n")) >= 0) {
        const blok = buf.slice(0, i);
        buf = buf.slice(i + 2);
        const olay = /^event: (.+)$/m.exec(blok)?.[1];
        const veri = /^data: (.+)$/m.exec(blok)?.[1];
        if (!olay || !veri) continue;
        const d = JSON.parse(veri);
        if (olay === "baglam") on.baglam(d.kaynaklar);
        else if (olay === "parca") on.parca(d.metin);
        else if (olay === "sonuc") { on.sonuc(d); bitti = true; }
        else if (olay === "hata") { on.hata(d.mesaj); bitti = true; }
      }
    }
  } catch {
    if (!signal?.aborted) on.hata(BAGLANTI_HATASI);
    return;
  }
  if (!bitti && !signal?.aborted) on.hata("Cevap yarıda kesildi. Lütfen tekrar deneyin.");
}

export async function kaynakGetir(anahtar: string): Promise<KaynakMetni> {
  const res = await fetch(`${API_URL}/kaynak?anahtar=${encodeURIComponent(anahtar)}`);
  if (!res.ok) throw new Error(res.status === 404 ? "Kaynak bulunamadı." : "Kaynak metni alınamadı.");
  return res.json();
}

export async function saglik(): Promise<{ son_kontrol?: string | null; parca_sayisi?: number | null } | null> {
  try {
    const res = await fetch(`${API_URL}/saglik`);
    return res.ok ? await res.json() : null;
  } catch {
    return null;
  }
}

export function tarih(iso?: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return isNaN(d.getTime()) ? iso : d.toLocaleDateString("tr-TR", { day: "numeric", month: "long", year: "numeric" });
}
