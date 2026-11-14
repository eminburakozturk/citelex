export interface KararOgesi {
  baslik: string;
  tarih: string;
  gerekce: string;
}

export interface KronolojiAdimi {
  tarih: string;
  baslik: string;
  detay: string;
}

export interface OdakKarti {
  baslik: string;
  etiket: string;
  aciklama: string;
}

export interface BaglantiOgesi {
  etiket: string;
  href: string;
  yerTutucu: boolean;
}

export const GELISTIRICI_VERISI = {
  kimlik: {
    basHarfler: "AD",
    adSoyad: "[Ad Soyad]",
    unvan: "[Ünvan / Hedef Rol]",
    altBaslik: "[Şehir · İletişim / E-posta]",
    biyografi:
      "[Kısa biyografi: 2-3 cümle — Türkçe mevzuat için ölçülebilir, atıf doğrulamalı soru-cevap sistemi Citelex hakkında geliştirici notu buraya gelecek.]",
    baglantilar: [
      { etiket: "GitHub", href: "#github-ekle", yerTutucu: true },
      { etiket: "LinkedIn", href: "#linkedin-ekle", yerTutucu: true },
      { etiket: "CV (PDF)", href: "#cv-ekle", yerTutucu: true },
    ] as BaglantiOgesi[],
  },
  odaklar: [
    {
      baslik: "Ölçülebilir Hibrit RAG",
      etiket: "Çekirdek",
      aciklama:
        "bge-m3 yoğun vektör + Türkçe BM25 seyrek arama (RRF k=60), mevzuat/karar ayrı kanalları, cümle düzeyinde [n] atıf doğrulama ve LangGraph ajan döngüsü.",
    },
    {
      baslik: "Değerlendirme ve CI Kapısı",
      etiket: "CI / Eval",
      aciklama:
        "56 soruluk test seti (30 soruluk ayrı kalibrasyon setiyle), claude-haiku-5.5 LLM hakemli sadakat denetimi ve her commit'te koşan BM25 regresyon kapısı.",
    },
    {
      baslik: "Otonom Takip ve Yayın",
      etiket: "Ürün",
      aciklama:
        "Günlük sürüm karşılaştırması ile kelime farkı günlüğü, Next.js statik arayüz, FastAPI SSE akışı, MCP sunucusu, Tauri 2 masaüstü/Android ve Docker + OpenTelemetry.",
    },
  ] as OdakKarti[],
  kararlar: [
    {
      baslik: "Çekirdeği LangChain veya Chroma'ya taşımadım",
      tarih: "13 Kasım · KARARLAR.md",
      gerekce:
        "Çalışan ve ölçülmüş RAG hattını gereksiz soyutlama katmanlarıyla sarmalamak kalite kazandırmaz, hata ayıklamayı zorlaştırır ve regresyon riski taşır. LangGraph yalnız ajan modunda, tek adımlı hatla aynı test setinde karşılaştırılarak eklendi.",
    },
    {
      baslik: "Aramayı mevzuat ve karar diye iki kanala ayırdım",
      tarih: "12 Kasım · KARARLAR.md",
      gerekce:
        "Tek havuzda arandığında KVKK Kurul kararları kendi içlerinde alıntıladıkları kanun maddelerini dışarı itiyordu (ör. KVKK m. 6 ilk 5'ten düşmüş, mevzuat isabeti 9/9'dan 8/9'a inmişti). İki kanallı yapıda mevzuat 9/9, karar 4/4 isabet sağladı.",
    },
    {
      baslik: "Bilmiyorum eşiğini 0,574 yerine 0,637'de tuttum",
      tarih: "12 Kasım · KARARLAR.md",
      gerekce:
        "30 soruluk kalibrasyon setinin 0,574 kuralı doğru cevap sayısını 31'den 34'e çıkarsa da geçerli atıflı yanlış cevapları artırdı (iş güvencesinde 30 yerine 50 işçi gibi). Hukuk alanında kendinden emin yanlış cevap, 'bilmiyorum' demekten pahalıdır.",
    },
    {
      baslik: "Değişiklik tespitini ham PDF baytıyla değil içerik hash'iyle yaptım",
      tarih: "12 Kasım · KARARLAR.md",
      gerekce:
        "mevzuat.gov.tr'nin GeneratePdf (wkhtmltopdf) çıktıları gömülü CreationDate yüzünden her indirmede farklı bayt üretiyor; ham dosya hash'i kullanılsaydı metin aynıyken her gün sahte değişiklik alarmı üretilirdi.",
    },
    {
      baslik: "Reranker'ı yayında kapalı, ajan modunu varsayılan açık tuttum",
      tarih: "13 Kasım · KARARLAR.md",
      gerekce:
        "bge-reranker-v2-m3 sıralamayı iyileştirse de (R@1 43→48/51) 16 çekirdek CPU'da soru başına 43–119 sn sürdüğü ve tek adımda uçtan uca doğruluğu değiştirmediği (40/50) için yayında kapalı bırakıldı. Ajan moduysa doğruluğu %80'den %88'e (44/50) çıkardığı için varsayılan açıldı.",
    },
  ] as KararOgesi[],
  kronoloji: [
    {
      tarih: "11–12 Kasım 2026",
      baslik: "Veri hattı, hibrit arama ve ilk değerlendirme",
      detay:
        "pdfplumber ile 11.5 pt gövde/dipnot ayrımı, KVKK 40 Kurul kararı çıkarıcı, bge-m3 + Türkçe BM25 (RRF k=60), SQLite sürüm deposu ve 52 soruluk ilk değerlendirme + kalibrasyon seti.",
    },
    {
      tarih: "13 Kasım 2026",
      baslik: "6331 İSG, API/Web, Hakem, CI, Reranker, Ajan, Tauri",
      detay:
        "FastAPI SSE akışı ve Next.js arayüz, OpenRouter zinciri + claude-haiku-5.5 sadakat hakemi, GitHub Actions BM25 regresyon kapısı, OpenTelemetry + Jaeger, /degisiklikler, /pano, bge-reranker-v2-m3, LangGraph ajan modu, MCP sunucusu ve Tauri 2 EXE/APK.",
    },
    {
      tarih: "14 Kasım 2026",
      baslik: "Geniş katman, Oracle ARM64 paketi ve arayüz yenilemesi",
      detay:
        "895 kanunluk geniş katman (44.843 parça) ve 0,05 yönlendirme farkı kuralı, OpenRouter devre kesici, Oracle Cloud Ampere ARM64 yayın paketi, WCAG AA erişilebilirlik ve Legal Editorial tasarım dili.",
    },
  ] as KronolojiAdimi[],
  teknolojiler: [
    "Python",
    "FastAPI",
    "Qdrant",
    "bge-m3",
    "LangGraph",
    "MCP",
    "SQLite",
    "Next.js",
    "Tailwind CSS",
    "Tauri 2",
    "OpenTelemetry",
    "Docker Compose",
    "GitHub Actions",
  ],
};
