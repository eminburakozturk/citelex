export const API_URL = (() => {
  const ham = process.env.NEXT_PUBLIC_API_URL;
  if (ham === "same-origin") return "";
  return ham ?? "http://127.0.0.1:8000";
})();

export type Tur = "kanun" | "yonetmelik" | "teblig" | "karar";

export interface Kaynak {
  no: number;
  atif: string;
  anahtar: string;
  belge_tur: string;
  baslik: string;
  alinti: string;
}

export type AdimAdi = "arama" | "esik" | "yeniden_yazma" | "llm" | "atif_dogrulama";
export type AdimDurumu = "tamam" | "atlandi" | "basarisiz";

export interface Adim {
  ad: AdimAdi;
  durum: AdimDurumu;
  detay: string;
  sure_sn: number;
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
  arama_sn?: number;
  llm_sn?: number;
  llm?: string;
  model?: string;
  gecersiz_atif?: number;
  ajan_deneme?: number;
  ajan_sorgular?: string[];
  adimlar?: Adim[];
}

export interface KaynakGecmisi {
  tarih: string;
  kanun: string;
  aciklama: string;
}

export interface IliskiliMadde {
  anahtar: string;
  atif?: string;
  baslik?: string;
  iliski: "atif_yapar" | "atif_alir";
}

export interface KaynakParcasi {
  fikra_no?: string | number | null;
  bolum?: string | null;
  metin: string;
  mulga?: boolean;
}

export interface KaynakMetni {
  anahtar: string;
  atif: string;
  belge_tur: string;
  belge_adi: string;
  baslik: string;
  metin?: string;
  parcalar?: KaynakParcasi[];
  karar_tarihi?: string | null;
  mulga: boolean;
  diger_kanuna_islendi?: boolean;
  dipnotlar: { no?: string | number; metin: string }[];
  url: string;
  son_kontrol: string | null;
  gecmis?: KaynakGecmisi[];
  iliskili?: IliskiliMadde[];
}

export interface RgBekleyen {
  gun: string;
  baslik: string;
  url: string;
  belge_id: string;
}

export interface SonDegisiklikOzeti {
  fark_id: string;
  zaman: string;
  belge_id: string;
}

export interface GuncellikBilgisi {
  son_kontrol: string | null;
  belge_sayisi: number;
  rg_bekleyen: RgBekleyen[];
  son_degisiklik: SonDegisiklikOzeti | null;
}

export interface SadeAciklama {
  anahtar: string;
  atif: string;
  maddeler: string[];
  ornek: string | null;
  uyari: string;
}

export interface Olaylar {
  onBaglam?: (kaynaklar: Kaynak[]) => void;
  onParca?: (metin: string) => void;
  onSonuc: (sonuc: Sonuc) => void;
  onHata: (mesaj: string) => void;
}

export async function sor(
  soru: string,
  turler: Tur[] | null,
  ajan: boolean,
  olaylar: Olaylar,
  signal?: AbortSignal,
): Promise<void> {
  const govde: { soru: string; turler?: Tur[]; ajan: boolean } = { soru, ajan };
  if (turler && turler.length > 0 && turler.length < 4) govde.turler = turler;

  let res: Response;
  try {
    res = await fetch(`${API_URL}/sor`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: JSON.stringify(govde),
      signal,
    });
  } catch (e) {
    if ((e as Error).name === "AbortError") return;
    olaylar.onHata("API sunucusuna ulaşılamadı.");
    return;
  }

  if (!res.ok || !res.body) {
    let mesaj = "İstek başarısız.";
    try {
      const veri = await res.json();
      if (veri?.detail) mesaj = veri.detail;
    } catch {
      /* boş */
    }
    olaylar.onHata(mesaj);
    return;
  }

  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = "";

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });

      let pos: number;
      while ((pos = buf.indexOf("\n\n")) !== -1) {
        const blok = buf.slice(0, pos);
        buf = buf.slice(pos + 2);
        let tur = "";
        const data: string[] = [];
        for (const satir of blok.split(/\r?\n/)) {
          if (satir.startsWith("event:")) tur = satir.slice(6).trim();
          else if (satir.startsWith("data:")) data.push(satir.slice(5).trim());
        }
        if (!tur || data.length === 0) continue;
        const payload = JSON.parse(data.join("\n"));
        if (tur === "baglam") olaylar.onBaglam?.(payload.kaynaklar ?? []);
        else if (tur === "parca") olaylar.onParca?.(payload.metin ?? "");
        else if (tur === "sonuc") olaylar.onSonuc(payload as Sonuc);
        else if (tur === "hata") olaylar.onHata(payload.mesaj ?? "Hata oluştu.");
      }
    }
  } catch (e) {
    if ((e as Error).name === "AbortError") return;
    olaylar.onHata("Akış kesildi.");
  }
}

export async function kaynakGetir(anahtar: string): Promise<KaynakMetni> {
  const res = await fetch(`${API_URL}/kaynak?anahtar=${encodeURIComponent(anahtar)}`);
  if (!res.ok) {
    throw new Error(res.status === 404 ? "Kaynak bulunamadı." : "Kaynak alınamadı.");
  }
  return res.json();
}

export async function saglik(): Promise<{ durum: string; son_kontrol?: string | null } | null> {
  try {
    const res = await fetch(`${API_URL}/saglik`);
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function guncellikGetir(): Promise<GuncellikBilgisi | null> {
  try {
    const res = await fetch(`${API_URL}/guncellik`);
    if (!res.ok) return null;
    return (await res.json()) as GuncellikBilgisi;
  } catch {
    return null;
  }
}

export async function aciklamaGetir(anahtar: string): Promise<SadeAciklama> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}/aciklama`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ anahtar }),
    });
  } catch {
    throw new Error("Açıklama servisine ulaşılamadı.");
  }
  if (!res.ok) {
    if (res.status === 404) {
      throw new Error("Sade açıklama özelliği şu an bu sunucuda etkin değil.");
    }
    let mesaj = "Sade açıklama alınamadı.";
    try {
      const j = await res.json();
      if (j?.detail) mesaj = String(j.detail);
    } catch {
      /* boş */
    }
    throw new Error(mesaj);
  }
  return (await res.json()) as SadeAciklama;
}

export async function ilgiliGetir(soru: string, anahtarlar: string[]): Promise<string[]> {
  if (!soru || anahtarlar.length === 0) return [];
  try {
    const res = await fetch(`${API_URL}/ilgili`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ soru, anahtarlar }),
    });
    if (!res.ok) return [];
    const veri = (await res.json()) as { sorular?: unknown };
    if (!Array.isArray(veri?.sorular)) return [];
    return veri.sorular.filter((x): x is string => typeof x === "string" && x.trim().length > 0);
  } catch {
    return [];
  }
}

export function tarih(iso?: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("tr-TR", { day: "numeric", month: "long", year: "numeric" });
}
