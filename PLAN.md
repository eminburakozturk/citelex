# Citelex — Kendini Güncelleyen, Kaynak Gösteren Mevzuat Asistanı (RAG)

## Amaç
Türk mevzuatı üzerine Türkçe soru-cevap yapan, her cevabı kaynak (kanun/yönetmelik/karar + madde) ve
güncellik tarihiyle veren, cevap yoksa "bilmiyorum" diyen bir RAG sistemi. Veri kaynaklarını her gün
kendisi kontrol eder; değişen dokümanları artımlı olarak yeniden işler, eski sürümleri saklar ve her
güncellemeden sonra kendini değerlendirme setiyle test eder.
Hedef kitle: kurumsal LLM / legal-tech, iç dokümanlarıyla canlı RAG kurmak isteyen her şirket.

## Kapsam (iki katman)
| Katman | İçerik | Kalite ölçümü |
|---|---|---|
| Derin | KVKK (6698), İş Kanunu (4857), İSG Kanunu (6331) + ilgili yönetmelik/tebliğler; KVKK Kurul karar özetleri (~350), ilke kararları, rehberler (PDF) | Değerlendirme seti (40–50 soru) |
| Geniş | Tüm kanunlar (~900) | Ölçülmez; README'de açıkça belirtilir |

Kapsam dışı (bilinçli): mahkeme kararları (Yargıtay/Danıştay/AYM), tüm yönetmelik/tebliğ evreni,
hukuk bürosu yayınları (telif). Mimari kapsam genişletmeye uygun kurulur.

## Kaynaklar
| Modül | Kaynak | Görev |
|---|---|---|
| `sources/mevzuat.py` | mevzuat.gov.tr (Mevzuat Bilgi Sistemi) | Kanun/yönetmelik/tebliğ güncel metni (ana doğruluk kaynağı) |
| `sources/kvkk.py` | kvkk.gov.tr: Kurul Karar Özetleri (/Icerik/5406), Kurul Kararları (/Icerik/5419), Rehberler (/Icerik/2030) | Kararlar ve rehberler |
| `sources/resmigazete.py` | resmigazete.gov.tr günlük fihrist (eskiler/YYYY/MM/YYYYMMDD.htm) | Erken uyarı / tetikleyici |
| `sources/hf_corpus.py` | Hugging Face `hasankursun/turkish-legislation-corpus` (899 kanun, CC-BY-4.0, Tem 2025'e kadar) | Geniş katmanın ilk kurulumu; güncellik mevzuat.gov.tr ile doğrulanır |

Not: KVKK Mart 2024'te değişti. Derin katman metinleri HER ZAMAN mevzuat.gov.tr'den alınır.

### Scraping kuralları
- Önce robots.txt kontrol edilir. İstekler arası 1–2 sn bekleme, tanımlayıcı User-Agent.
- Ham HTML/PDF `data/raw/` altında önbelleğe alınır (aynı sayfa gereksiz yere tekrar çekilmez).
- Her kaynak bağımsız modül: biri hata verirse diğerleri çalışır; hata günlüğe yazılır.
- Yeni modül önce 5 örnek dokümanla test edilir, yapı doğrulanınca tamamı çekilir.

## Mimari
```
sources/* -> ham veri (data/raw) -> normalize -> doküman deposu (SQLite: doküman, sürüm, içerik hash'i, tarih)
          -> parçalama (kanun: madde/fıkra; karar: bölüm/paragraf; rehber: başlık)
          -> embedding (bge-m3) -> Qdrant (dense) + BM25 (sparse) -> hibrit arama (+ ops. reranker)
          -> LLM (Gemini API / Ollama) -> cevap + kaynak + "son kontrol" tarihi

update/ (günlük zamanlayıcı):
  kaynakları kontrol et -> hash karşılaştır -> sadece değişenleri yeniden işle (upsert)
  -> eski sürümü "eski" işaretle (silme) -> değerlendirme setini çalıştır -> skor düştüyse uyar
  -> logs/updates.jsonl'e yaz
```

Metadata (her parça): kaynak, doküman_turu (kanun/yonetmelik/teblig/karar/rehber), doküman_no,
baslik, madde_no, fikra_no, surum, yururluk/yayın_tarihi, son_kontrol, url, katman (derin/genis).
Arayüzde doküman türüne göre filtre bulunur.

### Ürün katmanı (2026-11-13 kullanıcı kararı: hepsi ana plan, opsiyonel değil)
```
İstemciler:  web (Next.js statik çıktı)  |  Windows EXE + Android APK (Tauri 2, aynı arayüz)
                 |  HTTPS, akışlı cevap (SSE; Vercel AI SDK)
API (FastAPI):   /sor (tek adımlı hat)  /sor?mod=ajan (LangGraph)  /kaynak  /degisiklikler  /saglik
                 |
Arama:           iki kanallı hibrit (dense + BM25, RRF) -> reranker (bge-reranker-v2-m3; ölçülerek) -> bağlam
Üretim:          Gemini API (bulut) | Ollama (yerel geliştirme)
Depo:            SQLite sürüm deposu -> "bu madde değişti" (eski/yeni metin farkı)
Yayın:           Docker Compose (yerel) | Hugging Face Spaces (API + bge-m3 CPU) + Qdrant Cloud (ücretsiz katman)
CI:              GitHub Actions: testler + arama regresyonu (eval kapısı) + EXE/APK derleme
```
- Telefon/EXE istemcileri ince istemcidir: model cihazda çalışmaz (bge-m3 ~2,3 GB, LLM 7B), bulut API'ye bağlanır.
- Çekirdek hat (Qdrant, bge-m3, kendi hibrit araması, eval, güncelleme) framework'e TAŞINMAZ; LangGraph yalnız
  ajan modunda kullanılır ve tek adımlı hatla aynı eval setinde karşılaştırılır.
- API anahtarı yalnız sunucuda durur; istemcilere gömülmez. Halka açık API'de istek sınırı (rate limit) bulunur.

## Klasör yapısı
```
citelex/
  PLAN.md  CLAUDE.md  AGENTS.md  KARARLAR.md  README.md
  requirements.txt  Dockerfile  docker-compose.yml  .env.example  .gitignore
  src/
    sources/     # mevzuat.py, kvkk.py, resmigazete.py, hf_corpus.py
    store/       # SQLite doküman + sürüm deposu
    chunking/    # türe göre parçalayıcılar
    index/       # embedding, Qdrant, BM25
    retrieve/    # hibrit arama, filtre, reranker
    generate/    # prompt, LLM istemcileri (gemini, ollama)
    update/      # zamanlayıcı, değişiklik tespiti, artımlı pipeline
    agent/       # LangGraph ajan modu
    api/         # FastAPI (SSE akışlı cevap, kaynak, değişiklikler)
  web/           # Next.js arayüz (statik çıktı); web/src-tauri: Tauri 2 (EXE + APK)
  .github/workflows/   # CI: test, eval kapısı, EXE/APK derleme
  scripts/       # guncelle.ps1 (zamanlayıcı), yayın betikleri
  eval/          # questions.jsonl, run_eval.py
  results/       # değerlendirme tabloları -> git'e girer
  logs/          # güncelleme günlüğü (örnek kayıtlar git'e girer)
  data/          # git'e girmez
```

## Takvim
| Gün | Görev | Bitti kriteri | Ana araç |
|---|---|---|---|
| 11 Kas | 4 kaynak modülü; her biri 5 örnekle test, sonra derin katmanın tamamı | `data/raw` dolu, her kaynaktan doküman sayısı raporu | Claude Code |
| 12 Kas | Normalize + SQLite deposu (hash, sürüm) + türe göre parçalama + metadata | Parça sayısı ve 20 örnek parça elle kontrol edildi | Claude Code |
| 13 Kas | Embedding + Qdrant + BM25 hibrit arama; geniş katman embedding'i gece çalışır | 10 elle soruda doğru kaynak ilk 5'te | Claude Code |
| 14 Kas | LLM bağlantısı, kaynaklı cevap formatı, "bilmiyorum"; 40–50 soruluk eval seti (taslak ajan, doğrulama kullanıcı) | Uçtan uca soru-cevap + ilk eval tablosu | Claude Code |
| 15 Kas | Kendini güncelleme: zamanlayıcı (APScheduler / Görev Zamanlayıcı), hash ile değişiklik tespiti, artımlı upsert, sürümleme, eval regresyonu, günlük | Elle "sahte değişiklik" ile test: sadece değişen doküman yeniden işlendi | Claude Code |

Durum (13 Kas sabahı): 11–15 Kas satırlarının çekirdeği bitti (ayrıntı KARARLAR.md). Açık kalanlar aşağıda "Borçlar"da.

### Takvim v2 (2026-11-13; 16–17 Kas satırlarının yerine geçer)
| Gün | Görev | Bitti kriteri |
|---|---|---|
| 13 Kas | FastAPI: akışlı cevap (SSE), kaynak metni, sağlık ucu, istek sınırı; Docker Compose (API + Qdrant) | `docker compose up` ile API açılıyor; akışlı cevap curl ile görülüyor |
| 14 Kas | Next.js arayüz (Vercel AI SDK): akışlı sohbet, tıklanabilir kaynak paneli, tür filtresi, son kontrol tarihi, "hukuki tavsiye değildir" uyarısı; statik çıktı | Tarayıcıda uçtan uca soru-cevap; atıfa tıklayınca madde metni açılıyor |
| 15 Kas | Bulutta yayın: Hugging Face Spaces (API + bge-m3 CPU) + Qdrant Cloud + Gemini API; web arayüzü yayında | Herkese açık adresten soru-cevap çalışıyor |
| 16 Kas | Tauri 2: aynı arayüzden Windows EXE + Android APK (bulut API'ye bağlı) | EXE bilgisayarda, APK telefonda soru cevaplıyor |
| 17 Kas | "Bu madde değişti": sürüm deposundan değişiklik listesi + eski/yeni metin farkı (API + arayüz); reranker ölçümü | Sahte değişiklik arayüzde fark olarak görünüyor; reranker'lı/siz eval tablosu |
| 18 Kas | GitHub Actions: testler + arama regresyonu kapısı + EXE/APK otomatik derleme | Push'ta CI yeşil; isabeti düşüren değişiklik kırmızı |
| 19 Kas | LangGraph ajan modu (bağlam yetmiyorsa soruyu yeniden yazıp tekrar ara) + tek adımlı hatla eval karşılaştırması | Ajan ve tek adım aynı sette ölçüldü, sonuç tabloda |
| 20 Kas | Karşılaştırma deneyleri: dense/BM25/hibrit; madde/fıkra/hibrit; BM25 vs bge-m3 sparse; yerel vs API; Borçlar | results/ altında tablolar |
| 21 Kas | README (mimari şeması, sonuç tabloları, sınırlar, kurulum), repo public | Repo public, canlı bağlantı README'de |

Kapsam kesilmez; iş yetişmezse tarih kayar. Kesinti gerekirse kullanıcıya sorulur.
Kendini güncelleme ve değerlendirme setinden VAZGEÇİLMEZ.

### Borçlar (önceki günlerden)
- 6331 İSG Kanunu derlemde yok (kapsamda kalıp kalmayacağı kullanıcı kararı).
- Geniş katman (~900 kanun, HF corpus) kurulmadı; Qdrant Cloud ücretsiz katmanına (1 GB) sığıp sığmadığı ölçülmeli.
- `sources/resmigazete.py` (erken uyarı) ve `sources/hf_corpus.py` yazılmadı.
- Günlük görev Görev Zamanlayıcı'da oluşturulmadı (kullanıcı onayı bekliyor).
- Mevzuat PDF'i değişiklik yolu canlı test edilmedi.
- Eval seti kullanıcı doğrulaması bekliyor; Gemini ile eval çalıştırılmadı.

## Ortam
- Windows laptop, RTX 4060 Laptop (8 GB VRAM), 32 GB RAM. Conda ortamı: `citelex` (Python 3.11).
- Qdrant: Docker Desktop (yerel) / Qdrant Cloud (yayın). Yerel LLM: Ollama (qwen2.5:7b). API: Gemini (anahtar `.env`; kullanıcı sağlar).

## Kurallar
- Arayüzde ve README'de "Bu sistem hukuki tavsiye vermez" uyarısı.
- Değerlendirme setindeki beklenen cevaplar kullanıcı tarafından kaynak metinden doğrulanır.
- Tüm metrikler gerçek çalıştırmalardan gelir; uydurma sayı yok.
- API anahtarları sadece `.env` içinde; `.env` git'e girmez.
- Her mantıklı adım ayrı commit. Push'u kullanıcı yapar.
