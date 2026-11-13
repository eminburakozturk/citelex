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
İzleme:          her sorunun izi (arama, bağlam, gecikme, token/maliyet): Langfuse veya OpenTelemetry
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

### DEVAM NOKTASI (yeni oturum buradan başlar; bitince bu bölümü güncelle)
Son durum: 13 Kas akşamı. Biten: 6331 derlemde; eval seti 56 soru; **13 Kas satırı tamam** (FastAPI + Compose);
**14 Kas satırı tamam** (Next.js arayüz `web/`: akış, kaynak paneli, tür filtresi; tarayıcıda uçtan uca doğrulandı).
Çalıştırma: `docker compose up -d` (API 8000 + Qdrant), `npm --prefix web run dev` (3000). Statik çıktı: `npm --prefix web run build` -> `web/out`.
15 Kas (bulutta yayın) YARIM: Qdrant Cloud'da indeks kurulu; yayın betikleri hazır (scripts/yayin_qdrant.py,
scripts/yayin_space.py); yapılandırma yerelde bulut Qdrant'a karşı doğrulandı. ENGEL: Hugging Face Docker Space artık PRO
abonelik istiyor (402) -> barındırma kararı kullanıcıda. Ayrıca Gemini ücretsiz kota günde 20 istek -> çözüm olarak
OpenRouter sağlayıcısı eklendi (model zincirli; deepseek-v4.1-flash 40/50 %80, ücretsiz nemotron 39/50 %78; yerel qwen2.5
33/50). Zincir OPENROUTER_MODELS ile .env'ten seçilir; kalıcı model/faturalama + barındırma kararı kullanıcıda.
Sıradaki işler, sırayla ve DURMADAN:
1. 16 Kas satırı (GitHub Actions + arama regresyonu kapısı, LLM hakemli sadakat, izlenebilirlik).
2. Kullanıcının barındırma/model kararına göre yayını bitir.
3. Takvim v2'nin kalan satırları (17, 18, 19, 20, 21 Kas).
Kullanıcıdan beklenenler: eval setinin doğrulanması (56 soru, 4'ü yeni İSG sorusu); barındırma (HF PRO / alternatif) ve
kalıcı LLM (ücretsiz nemotron zinciri / ücretli deepseek / Gemini faturalama) kararları.
Günlük görev kurulu ("Citelex Gunluk Guncelleme", her gün 03:00, scripts/guncelle.ps1).

### Takvim v2 (2026-11-13; 16–17 Kas satırlarının yerine geçer)
Hedef rol: yapay zekâ / ürün geliştirici. Sıra CV değerine göre: önce canlı ve ölçülen sistem, sonra
LLM mühendisliği sinyalleri; EXE + APK "mobilde de varım" göstergesi olarak en sonda ve sade tutulur.

| Gün | Görev | Bitti kriteri |
|---|---|---|
| 13 Kas | FastAPI: akışlı cevap (SSE), kaynak metni, sağlık ucu, istek sınırı; Docker Compose (API + Qdrant) | `docker compose up` ile API açılıyor; akışlı cevap curl ile görülüyor |
| 14 Kas | Next.js arayüz (Vercel AI SDK): akışlı sohbet, tıklanabilir kaynak paneli, tür filtresi, son kontrol tarihi, "hukuki tavsiye değildir" uyarısı; statik çıktı | Tarayıcıda uçtan uca soru-cevap; atıfa tıklayınca madde metni açılıyor |
| 15 Kas | Bulutta yayın: Hugging Face Spaces (API + bge-m3 CPU) + Qdrant Cloud + Gemini API; web arayüzü yayında | Herkese açık adresten soru-cevap çalışıyor |
| 16 Kas | GitHub Actions: testler + arama regresyonu kapısı; eval'e LLM hakemli sadakat ölçütü (cevap kaynağa dayanıyor mu; anahtar kelime ölçütünün yanlış pozitiflerine karşı); izlenebilirlik (her sorunun araması, bağlamı, gecikmesi, token/maliyeti kayıtlı; Langfuse veya OpenTelemetry) | Push'ta CI yeşil, isabeti düşüren değişiklik kırmızı; bir sorunun izi panelde görülüyor; eval raporunda sadakat sütunu, hakemin 10 cevapta elle kontrolü |
| 17 Kas | "Bu madde değişti": sürüm deposundan değişiklik listesi + eski/yeni metin farkı (API + arayüz); reranker ölçümü | Sahte değişiklik arayüzde fark olarak görünüyor; reranker'lı/siz eval tablosu |
| 18 Kas | Ortak araç katmanı (`mevzuat_ara`, `madde_getir`): aynı araçlar hem LangGraph ajan modunda hem MCP sunucusunda (`src/mcp_server.py`); LangGraph ajan modu (bağlam yetmiyorsa soruyu yeniden yazıp tekrar ara) + tek adımlı hatla eval karşılaştırması | Ajan ve tek adım aynı sette ölçüldü, sonuç tabloda; MCP sunucusu bir MCP istemcisinden çağrılıp atıflı sonuç döndürüyor |
| 19 Kas | Karşılaştırma deneyleri: dense/BM25/hibrit; madde/fıkra/hibrit; BM25 vs bge-m3 sparse; yerel vs API; Borçlar; arayüzde değerlendirme panosu (doğruluk, yanlış "bilmiyorum", eşik etkisi, çalıştırma geçmişi) | results/ altında tablolar; pano gerçek eval çıktılarını gösteriyor |
| 20 Kas | Tauri 2: aynı arayüzden Windows EXE + Android APK (ince istemci, bulut API'ye bağlı); CI'da otomatik derleme | EXE bilgisayarda, APK telefonda soru cevaplıyor |
| 21 Kas | README (mimari şeması, sonuç tabloları, sınırlar, kurulum, canlı bağlantı), repo public | Repo public |

CV'ye yönelik üç ek (2026-11-13) yeni gün açmadan ilgili satırlara yerleştirildi: LLM hakemli sadakat ölçütü (16 Kas),
MCP sunucusu (18 Kas, ajanla ortak araç katmanı), değerlendirme panosu (19 Kas). OCR eklenmedi (KARARLAR.md).
Kapsam kesilmez; iş yetişmezse tarih kayar. Kesinti gerekirse kullanıcıya sorulur.
Kendini güncelleme ve değerlendirme setinden VAZGEÇİLMEZ.

### Borçlar (önceki günlerden)
- Geniş katman (~900 kanun, HF corpus) kurulmadı; Qdrant Cloud ücretsiz katmanına (1 GB) sığıp sığmadığı ölçülmeli.
- `sources/resmigazete.py` (erken uyarı) ve `sources/hf_corpus.py` yazılmadı.
- Mevzuat PDF'i değişiklik yolu canlı test edilmedi.
- Eval seti kullanıcı doğrulaması bekliyor.
- Gemini ile tam eval yapılamadı (ücretsiz kota günde 20 istek); model/faturalama kararı kullanıcıda.
- madde/fikra koleksiyonları 6331 ve bent parçalamasıyla güncellenmedi (19 Kas'ta yeniden kurulacak).
- Günlük toplam istek tavanı (CITELEX_GUNLUK_TOPLAM) yayından önce Gemini günlük kotasına göre ayarlanmalı.
- HF Spaces'te bge-m3'ün yalnız gereken dosyaları indirilmeli (tam depo 4,3 GB, ~20 dk).

## Ortam
- Windows laptop, RTX 4060 Laptop (8 GB VRAM), 32 GB RAM. Conda ortamı: `citelex` (Python 3.11).
- Qdrant: Docker Desktop (yerel) / Qdrant Cloud (yayın). Yerel LLM: Ollama (qwen2.5:7b). API: Gemini (anahtar `.env`; kullanıcı sağlar).

## Kurallar
- Arayüzde ve README'de "Bu sistem hukuki tavsiye vermez" uyarısı.
- Değerlendirme setindeki beklenen cevaplar kullanıcı tarafından kaynak metinden doğrulanır.
- Tüm metrikler gerçek çalıştırmalardan gelir; uydurma sayı yok.
- API anahtarları sadece `.env` içinde; `.env` git'e girmez.
- Her mantıklı adım ayrı commit. Push'u kullanıcı yapar.
