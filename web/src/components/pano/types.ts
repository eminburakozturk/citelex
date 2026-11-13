export interface SadakatOzeti {
  hakem: string | null;
  dosya: string;
  cevap: number;
  sadik: number;
  sadik_orani: number | null;
  destekli: number;
  kismen: number;
  desteksiz: number;
  n_iddia: number;
  destekli_orani: number | null;
}

export interface ModelOzeti {
  llm: string;
  tag: string;
  tarih: string;
  commit: string;
  n_ic: number;
  n_dis: number;
  baglam: number;
  atif: number;
  icerik: number;
  dogru: number;
  dogru_orani: number | null;
  yanlis_ret: number;
  yanlis_ret_orani: number | null;
  dogru_ret: number;
  dogru_ret_orani: number | null;
  gecersiz_atif: number;
  hata: number;
  medyan_sure_sn: number | null;
  sadakat: SadakatOzeti | null;
}

export interface GecmisKaydi {
  tarih: string;
  llm: string;
  commit: string;
  n_ic: number;
  n_dis: number;
  baglam: number;
  atif: number;
  icerik: number;
  dogru: number;
  dogru_orani: number | null;
  yanlis_ret: number;
  dogru_ret: number;
  gecersiz_atif: number;
  hata: number;
  tam: boolean;
}

export interface SoruSonucu {
  dogru: boolean;
  hata?: boolean;
  baglam?: boolean;
  atif?: boolean;
  icerik?: boolean;
  yanlis_ret?: boolean;
  dogru_ret?: boolean;
  katman?: string | null;
  sure_sn?: number | null;
  sadik?: boolean | null;
}

export interface SoruSatiri {
  id: string;
  tur: string;
  soru: string;
  sonuclar: Record<string, SoruSonucu>;
}

export interface PanoVerisi {
  uretim_tarihi: string;
  modeller: ModelOzeti[];
  gecmis: GecmisKaydi[];
  sorular: SoruSatiri[];
}

export function kisaModelAdi(llm: string): string {
  const [, ad = llm] = llm.includes(":") ? [llm.split(":")[0], llm.slice(llm.indexOf(":") + 1)] : ["", llm];
  return ad.replace(/^[^/]+\//, "").replace(/:free$/, " (free)");
}

export function saglayiciAdi(llm: string): string {
  const idx = llm.indexOf(":");
  return idx > 0 ? llm.slice(0, idx) : "";
}

export function yuzde(oran: number | null | undefined): string {
  if (oran == null) return "—";
  return `%${Math.round(oran * 100)}`;
}

export function tarihSaat(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleString("tr-TR", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}
