import { API_URL } from "@/lib/api";

export type BirimDurumu = "degisti" | "eklendi" | "silindi";
export type FarkParcasi = ["=" | "-" | "+", string];

export interface SurumBilgisi {
  surum_id: number;
  ilk_gorulme: string;
  hash: string;
}

export interface DegisiklikOzetiSayilari {
  degisti: number;
  eklendi: number;
  silindi: number;
}

export interface BirimOzeti {
  birim: string;
  etiket: string;
  durum: BirimDurumu;
}

export interface BirimAyrintisi extends BirimOzeti {
  eski: string | null;
  yeni: string | null;
  fark: FarkParcasi[];
}

export interface DegisiklikKaydi {
  fark_id: string;
  zaman: string;
  doc_key: string;
  belge_id: string;
  tur: string;
  eski: SurumBilgisi;
  yeni: SurumBilgisi;
  ozet: DegisiklikOzetiSayilari;
  birimler: BirimOzeti[];
}

export interface DegisiklikAyrintisi extends Omit<DegisiklikKaydi, "birimler"> {
  url?: string | null;
  birimler: BirimAyrintisi[];
}

export interface DegisikliklerYaniti {
  degisiklikler: DegisiklikKaydi[];
  son_kontrol?: string | null;
}

interface OrnekVeri {
  son_kontrol?: string | null;
  degisiklikler: DegisiklikKaydi[];
  ayrintilar: Record<string, DegisiklikAyrintisi>;
}

export const ORNEK_MODU = process.env.NEXT_PUBLIC_DEGISIKLIK_ORNEK === "1";

const BOLUM_ADI: Record<string, string> = {
  sikayet: "Şikâyet / ihlal bildirimi",
  savunma: "Veri sorumlusunun savunması",
  degerlendirme: "Kurulun değerlendirmesi",
  hukum: "Kurulun kararı",
};

const TUR_ADI: Record<string, string> = {
  karar: "Kurul kararı",
  mevzuat: "Mevzuat",
  kanun: "Kanun",
  yonetmelik: "Yönetmelik",
  teblig: "Tebliğ",
};

export function turAdi(tur: string): string {
  return TUR_ADI[tur] ?? tur;
}

export function birimEtiketi(etiket: string): string {
  return BOLUM_ADI[etiket] ?? etiket;
}

export function belgeBasligi(docKey: string, belgeId: string): string {
  if (docKey.startsWith("karar:")) {
    return `KVKK Kurul Kararı ${docKey.slice("karar:".length).replace("-", "/")}`;
  }
  return belgeId || docKey;
}

export function zamanMetni(iso?: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleString("tr-TR", {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

let ornekCache: OrnekVeri | null = null;

async function ornekGetir(): Promise<OrnekVeri> {
  if (ornekCache) return ornekCache;
  const res = await fetch("/degisiklik_ornek.json");
  if (!res.ok) throw new Error("Örnek değişiklik verisi yüklenemedi.");
  ornekCache = (await res.json()) as OrnekVeri;
  return ornekCache;
}

export async function degisiklikleriGetir(limit = 20): Promise<DegisikliklerYaniti> {
  if (ORNEK_MODU) {
    const o = await ornekGetir();
    return { degisiklikler: o.degisiklikler.slice(0, limit), son_kontrol: o.son_kontrol };
  }
  let res: Response;
  try {
    res = await fetch(`${API_URL}/degisiklikler?limit=${limit}`);
  } catch {
    throw new Error("Değişiklik kayıtları alınamadı. API sunucusuna ulaşılamadı.");
  }
  if (!res.ok) throw new Error("Değişiklik kayıtları alınamadı.");
  return res.json();
}

export async function degisiklikAyrintisiGetir(farkId: string): Promise<DegisiklikAyrintisi> {
  if (ORNEK_MODU) {
    const o = await ornekGetir();
    const d = o.ayrintilar[farkId];
    if (!d) throw new Error("Değişiklik ayrıntısı bulunamadı.");
    return d;
  }
  let res: Response;
  try {
    res = await fetch(`${API_URL}/degisiklik/${encodeURIComponent(farkId)}`);
  } catch {
    throw new Error("Değişiklik ayrıntısı alınamadı. API sunucusuna ulaşılamadı.");
  }
  if (!res.ok) {
    throw new Error(res.status === 404 ? "Değişiklik kaydı bulunamadı." : "Değişiklik ayrıntısı alınamadı.");
  }
  return res.json();
}
