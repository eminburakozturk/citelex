[![CI](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml/badge.svg)](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml)

# Citelex — Türk Mevzuatı için Kaynak Gösteren RAG

**Citelex**, Türk iş hukuku ve kişisel verilerin korunması alanındaki derin katman mevzuatını (`12` mevzuat belgesi ve `40` seçili KVKK Kurul kararı; toplam `52` belge) ve gerektiğinde `895` kanunluk (`44.843` parça) geniş katmanı madde/fıkra düzeyinde dizinleyip her iddiayı resmi kaynağa dayandırarak yanıtlayan, kaynak değiştikçe kendini güncelleyebilen ve kanıt yetersiz kaldığında `"bilmiyorum"` diyebilen bir RAG sistemidir.

> **Uyarı:** Bu sistem hukuki tavsiye vermez; yalnızca dizinlenen mevzuat ve kurul kararları üzerinden kaynak göstererek bilgi sunar.

## Mimari

![](docs/mimari.svg)

## Ekranlar

**Kaynaklı yanıt ve madde paneli** — `[n]` atıflarına tıklandığında ilgili kanun/yönetmelik/karar metni, değişiklik geçmişi ve ilişkili maddeler ağı yan panelde açılır:

![Kaynaklı yanıt ve açık kaynak paneli](docs/ekran/01_cevap.png)

![İlişkili maddeler bağlantı ağı ve listesi](docs/ekran/01_iliskili.png)

**Geniş katman uyarısı ve kapsam dışı reddi** — Derin katman eşiği geçemediğinde ~900 kanunluk geniş katman devreye girer ve doğrulanmamış katman uyarısı gösterilir; derlemle ilgisiz sorular reddedilir:

![Geniş katman rozeti ve uyarısı](docs/ekran/02_genis.png)

**Değerlendirme panosu ve değişiklik takibi** — Model/yapılandırma karşılaştırması (`/pano`) ile eski–yeni sürüm kelime farkı (`/degisiklikler`):

![Değerlendirme panosu](docs/ekran/04_pano.png)

![Madde değişikliği kelime farkı](docs/ekran/05_degisiklik.png)

Diğer ekranlar: [Kapsam dışı ret](docs/ekran/03_bilmiyorum.png) · [Mobil görünüm](docs/ekran/06_mobil.png) · [Jaeger / OpenTelemetry izi](docs/ekran/07_jaeger.png)

## Sonuçlar

### Model ve yapılandırma karşılaştırması (`56` soru: `50` kapsam içi, `6` kapsam dışı)

| Model (yapılandırma) | Doğru | Tam destekli sadakat | İddia desteği | Yanlış "bilmiyorum" | Kapsam dışı ret | Medyan süre |
|---|---:|---:|---:|---:|---:|---:|
| **`openrouter:deepseek/deepseek-v4.1-flash-1017` (yayın: ajan + geniş katman, reranker kapalı)** | **44/50 (%88)** | **45/50 (%90)** | 184/190 (%97) | 0/50 (%0) | 5/6 (%83)¹ | 2,23 sn |
| `openrouter:deepseek/deepseek-v4.1-flash-1017` (ajan + reranker) | 45/50 (%90) | 46/50 (%92) | 181/185 (%98) | 0/50 (%0) | 6/6 (%100) | 3,98 sn |
| `openrouter:deepseek/deepseek-v4.1-flash-1017` (ajan) | 44/50 (%88) | 46/49 (%94) | 177/182 (%97) | 1/50 (%2) | 6/6 (%100) | 2,42 sn |
| `openrouter:deepseek/deepseek-v4.1-flash-1017` (reranker) | 40/50 (%80) | — | — | 7/50 (%14) | 6/6 (%100) | 3,66 sn |
| `openrouter:deepseek/deepseek-v4.1-flash-1017` (tek adım) | 40/50 (%80) | 41/43 (%95) | 161/163 (%99) | 7/50 (%14) | 6/6 (%100) | 1,90 sn |
| `openrouter:qwen/qwen3.7-flash` (tek adım) | 39/50 (%78) | 26/42 (%62) | 145/162 (%90) | 8/50 (%16) | 6/6 (%100) | 2,39 sn |
| `openrouter:nvidia/nemotron-3-ultra-550b-a55b:free` (tek adım) | 39/50 (%78) | 35/42 (%83) | 86/93 (%92) | 8/50 (%16) | 6/6 (%100) | 2,43 sn |
| `ollama:qwen2.5:7b` (tek adım) | 33/50 (%66) | — | — | 12/50 (%24) | 6/6 (%100) | 2,86 sn |

¹ *Geniş katman açıkken "kapsam dışı" etiketli `d03` (ve bir önceki koşuda `d05`) geniş katmandaki 7036 s. Kanun m.3 ve 6102 s. TTK m.338'den doğru ve atıflı cevaplanıyor; etiketleri geçersizleşti (uydurma cevap değil). Aynı yapılandırmanın iki koşusu arasında sadakat 47 -> 45/50, kapsam dışı ret 4 -> 5/6 oynadı (arama artık deterministik; fark LLM'den): ±2 soruluk farklar gürültü düzeyindedir.*

*Kaynak: `results/eval_history.jsonl`, `results/eval_*.md`, `results/sadakat_*__hakem_openrouter_anthropic_claude_haiku_5.5.jsonl` ve `KARARLAR.md`. Tüm çalıştırmalarda geçersiz atıf `0`'dır.*

### Varsayılan çalışma ve OpenRouter devre kesici

- **Yerel (GPU) vs yayın (CPU) varsayılanı:** En yüksek ölçüm **ajan + reranker** (`45/50`, `KARARLAR.md`) olduğundan yerel GPU ortamında ikisi birlikte varsayılan açıktır. Ancak `bge-reranker-v2-m3` 16 çekirdek CPU'da sorgu başına `43,0–118,9 sn` (`43,0 / 118,9 / 42,9 sn`, `KARARLAR.md`) sürdüğü için `docker-compose.yml` / CPU yayında `CITELEX_RERANK=0` ile kapalı tutulur ve yalnızca **ajan modu** (`44/50`, medyan `2,42 sn`) varsayılan çalışır.
- **OpenRouter zinciri ve devre kesici:** `OPENROUTER_MODELS` içindeki modeller sırayla denenir (ör. ücretsiz kota dolunca ücretli yedeğe geçer). Günlük kota `429` hatasında ilgili model `1 saat`, diğer `429`'larda `60 sn` devre dışı bırakılır (`KARARLAR.md`).
- **Canlı demo zinciri:** `nemotron-3-ultra:free → deepseek-v4.1-flash → qwen3.7-flash` (önce ücretsiz; kota dolunca en sadık ölçülen ücretli model `deepseek`, o da yanıt vermezse en ucuz `qwen`). Tablodaki "yayın" satırı `deepseek` ile ölçüldü; canlı demoda cevabı çoğunlukla ücretsiz model verir ve bu modelle ajan + geniş katman yapılandırması ayrıca ölçülmedi (tek adımda `39/50`, tam destekli sadakat `%83`). Ücretli modele düşülürse maliyet: gerçek iz kayıtlarında soru başına medyan `~4.500` girdi / `~200` çıktı token'ı; OpenRouter fiyatlarıyla (17 Kas 2026) soru başına `qwen` `~$0,00017`, `deepseek` `~$0,00028`; günlük `300` soru tavanında ayda `~$1,5` / `~$2,5`.

### Reranker geri getirme ölçümü ve arama deneyleri

| Yöntem (geri getirme) | Alt küme | R@1 | R@3 | R@5 | MRR |
|---|---|---:|---:|---:|---:|
| Hibrit (bge-m3 + BM25, RRF k=60) | Mevzuat (`n=51`) | 44/51 | 48/51 | 48/51 | 0,908 |
| Hibrit + reranker (`30` aday) | Mevzuat (`n=51`) | 48/51 | 49/51 | 50/51 | 0,957 |
| Hibrit | KVKK kararı (`n=12`) | 11/12 | 12/12 | 12/12 | 0,958 |
| Hibrit + reranker (`30` aday) | KVKK kararı (`n=12`) | 12/12 | 12/12 | 12/12 | 1,000 |

*Kaynak: `results/rerank_compare.md` (GPU fp16 medyan `0,74–1,45 sn/sorgu`, iki koşu). Parçalama × yöntem ve BM25 vs `bge-m3` sparse karşılaştırmaları `results/compare_retrieval.md` dosyasındadır.*

### CI arama kapısı temel değerleri

- **BM25 (bellek içi fixture):** mevzuat `48/51`, KVKK kararı `12/12`
- **Qdrant (hibrit):** mevzuat `48/51`, KVKK kararı `12/12`

*Kaynak: `eval/gate_baseline.json`.*

## Değerlendirme Yöntemi ve Sınırlar

- **Soru seti ve içerik ölçütü:** `56` soruluk ana set ile `18` soruluk geniş setin beklenen kaynak ve kanıtları resmî metinle elle doğrulandı (`74/74`, `eval/DOGRULAMA.md`; geliştirici kontrolü, hukukçu incelemesi değildir); `icerik` ölçütü anahtar kelime eşleşmesine dayanır (`KARARLAR.md`).
- **Hakem kararlılığı:** LLM hakem (`anthropic/claude-haiku-5.5`) üzerindeki `10` kararlık elle kontrolde `9` uyum görülmüştür; asıl sadakat ölçütü tüm iddiaların desteklendiği `tam_destekli` oranıdır (`KARARLAR.md`).
- **Eşik tercihi:** Kalibrasyon `30` soruluk ayrı sette yapılmış; `0,574` yerine `0,637` eşiği seçilmiştir (`KARARLAR.md`, `results/calibration.md`). Tutucu eşik kısa/genel kapsam içi soruları reddedebilir; ajan modu bu oranı `7/50`'den `1/50`'ye düşürür.
- **Geniş katman (`895` kanun, `44.843` parça; HF korpusu, Temmuz 2025'e kadar):** doğruluğu tam setle ölçülmedi, cevaplar `"Geniş katman · doğruluğu ölçülmedi"` rozetiyle döner (`CITELEX_GENIS=0` kapatır).
  - *Yönlendirme:* derin katman `0,637` eşiğini geçemezse **veya** geniş katman derin katmandan `0,05`'ten fazla öndeyse. `0,05`, eval setlerinden bağımsız `eval/calibration.jsonl` üzerinde derin katman sorularında görülen en büyük geniş üstünlüğün (`+0,021`) yaklaşık iki katıdır.
  - *Derin katmana etkisi (56 soru):* kapsam içi `45/50` değişmedi. Kapsam dışı ret `6/6 -> 5/6`: "kapsam dışı" etiketli `d03` artık geniş katmandaki `7036` s. Kanun m.3'ten **doğru ve atıflı** cevaplanıyor (etiket geçersizleşti, uydurma değil). Medyan süre `3,98 -> 5,47 sn`.
  - *Geniş set, küçük örneklem (`eval/genis_sorular.jsonl`, 15 + 3 soru, `results/genis_check.md`):* R@1 `8/15`, R@5 `14/15`, yönlendirme `14/15`, beklenen madde bağlamda `13/15`, kapsam dışı ret `3/3`. Kalan sınırlar: `g02` eşiğin hemen altında (`0,629`), `g08` ilk 5'te yok. `g13` fark kuralını bulduran örnek olduğu için set bu kural açısından bağımsız değildir.

## Kendini güncelleme

- **Günlük hat (`src/update/run.py`, her gün 03:00):** 52 kaynağı indirir; ayrıştırılmış metnin hash'i değişmediyse durur (PDF baytları her indirmede değişir). Değişen belge yeniden ayrıştırılır, Qdrant **artımlı** güncellenir (yalnız değişen parçalar embed edilir), eski sürüm silinmez, madde/bölüm düzeyinde kelime farkı üretilir (`/degisiklikler`) ve arama regresyonu çalışır.
- **Resmî Gazete erken uyarı (`src/update/erken_uyari.py`):** son 3 günün fihristi taranır; derin katman kanunlarını değiştiren torba kanunlar metinden yakalanır (ör. 7499 s. Kanun → KVKK m.6). Resmî Gazete'de olup mevzuat.gov.tr'ye henüz işlenmemiş değişiklik "bekleyen" olarak raporlanır.
- **Doğrulama:** sahte bir değişiklikle (`--sahte`) uçtan uca denendi; bu deneme farkları arayüzde **"Test kaydı"** olarak işaretlenir, gerçek değişiklik sayılmaz.

## Yayın

Tek sanal makinede (Oracle Cloud Always Free, ARM): Qdrant + API + Caddy (otomatik HTTPS) ve gece çalışan güncelleme servisi. Paketleme, kurulum ve duman testi: [deploy/oracle/README.md](deploy/oracle/README.md). Yayında reranker kapalıdır (CPU'da ~43 sn/sorgu); ajan ve geniş katman açıktır.

## Veri kaynakları

| Kaynak | Kullanım | Not |
|---|---|---|
| [mevzuat.gov.tr](https://www.mevzuat.gov.tr) | Derin katman kanun, yönetmelik ve tebliğ metinleri (güncel metin) | Resmî mevzuat metinleri; günlük kontrol edilir |
| [kvkk.gov.tr](https://www.kvkk.gov.tr) | 40 seçili KVKK Kurul karar özeti | Günlük kontrol edilir |
| [resmigazete.gov.tr](https://www.resmigazete.gov.tr) | Erken uyarı (günlük fihrist) | Yalnız başlık ve ilgili metin taranır |
| [hasankursun/turkish-legislation-corpus](https://huggingface.co/datasets/hasankursun/turkish-legislation-corpus) | Geniş katman (~900 kanun, Temmuz 2025'e kadar) | **CC-BY-4.0**; atıf zorunludur |

Kaynak sitelere istekler `robots.txt` kurallarına uyularak, tanımlayıcı bir User-Agent ile ve host başına en az 2 sn arayla gönderilir.

## Kurulum

### 1. Ortam ve bağımlılıklar

```bash
conda activate citelex
# veya temiz Python 3.11 ortamında (önce donanıma uygun torch, ardından requirements.txt):
# pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cu126   # CPU için: .../whl/cpu
# pip install -r requirements.txt
```

`.env` dosyasını `.env.example` şablonundan oluşturun (`cp .env.example .env`) ve değerleri kendi anahtarlarınızla doldurun:

- **Model / arama:** `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `OPENROUTER_MODELS`, `OLLAMA_HOST`, `CITELEX_LLM`, `QDRANT_URL`
- **Hız sınırı / CORS:** `CITELEX_RATE_DK`, `CITELEX_RATE_GUN`, `CITELEX_GUNLUK_TOPLAM`, `CITELEX_TRUST_PROXY`, `CITELEX_CORS`

### 2. Altyapı, veri hazırlama ve indeksleme

`data/` dizini `.gitignore` kapsamındadır; temiz bir `git clone` sonrasında önce harici Qdrant volume'ü oluşturulur ve `52` ham kaynak belgesi (`12` mevzuat PDF + `40` KVKK Kurul kararı) indirilir:

```bash
docker volume create citelex_qdrant
docker compose up -d qdrant

# Ham belgeleri indir (mevzuat.gov.tr + kvkk.gov.tr; host başına ~2 sn bekleme ile ~2,5 dk):
python -c "from pathlib import Path; import httpx; from src.update.run import tracked, fetch_raw
with httpx.Client() as c:
    for d in tracked():
        p = Path(d['local_path']); p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists(): p.write_bytes(fetch_raw(d, c)); print(d['doc_key'], flush=True)"

python -m src.ingest.parse
python -m src.ingest.iliskiler
python -m src.ingest.chunk --mode hibrit --max-chars 1500
python -m src.ingest.parse_karar
python -m src.index.build --mode hibrit --recreate
python -m src.update.run --init
```

### 3. API, Web arayüzü ve izlenebilirlik

`web/src` statik çıktı üretir ve arayüzde sohbet dışında **`/pano`** (değerlendirme panosu), **`/degisiklikler`** (madde/bölüm kelime farkı) ve **`/yontem`** (2 dakikalık mimari/ölçüm özeti) sayfalarını sunar:

```bash
npm --prefix web ci               # temiz klonda web bağımlılıklarını kurar
npm --prefix web run build        # web/out/ üretir; Compose api'si /app/web/out üzerinden sunar
docker compose up -d api          # http://127.0.0.1:8000/
# duman testi: python scripts/duman_testi.py http://127.0.0.1:8000
# geliştirme modu: npm --prefix web run dev
# Jaeger izleri (http://127.0.0.1:16686): docker compose --profile izleme up -d
```

### 4. Masaüstü (Windows) ve Mobil (Android) istemci + MCP

- **Tauri 2 ince istemci (`desktop/`):** Aynı `web/out` arayüzünü paketler (Windows EXE `8,7 MB`, MSI `3,0 MB`, NSIS `2,0 MB`, Android arm64 APK `10,7 MB` — `KARARLAR.md`). Kurulum ve imza adımları için bkz. [desktop/README.md](desktop/README.md).
- **MCP sunucusu (`src/mcp_server.py`):** `mcp` stdio üzerinden `mevzuat_ara` ve `madde_getir` araçlarını sunar (`claude_desktop_config.json` içinde `"command": "python", "args": ["-m", "src.mcp_server"]`).

## Proje Yapısı

```text
citelex/
├── src/
│   ├── api/            # FastAPI + SSE, hız sınırı, /degisiklikler, /kaynak, statik web sunumu
│   ├── ingest/         # PDF/HTML/HF ayrıştırma ve hibrit madde/fıkra/ek parçalama
│   ├── index/          # bge-m3 dense + Türkçe BM25 sparse Qdrant indeksi (derin + geniş)
│   ├── retrieve/       # İki kanallı arama, eşik kapısı, bge-reranker-v2-m3, geniş katman
│   ├── generate/       # OpenRouter zinciri + devre kesici, prompt, atıf doğrulama, madde açıklama
│   ├── sources/        # mevzuat.gov.tr, kvkk.gov.tr, Resmî Gazete, HF korpusu
│   ├── update/         # Günlük hat, sürüm deposu (SQLite), kelime/madde farkı, erken uyarı
│   ├── agent.py        # LangGraph ajan modu (yeniden yazıp tekrar arama)
│   ├── tools.py        # Ortak araçlar (API, ajan ve MCP aynı kodu kullanır)
│   ├── trace.py        # OpenTelemetry izleri
│   └── mcp_server.py   # MCP sunucusu (mevzuat_ara, madde_getir)
├── eval/               # Kalibrasyon, değerlendirme, LLM hakem, CI arama kapısı, doğrulama listesi
├── scripts/            # Pano verisi, yayın paketi, duman testi
├── results/            # Eval, sadakat, rerank ve arama deneyi çıktıları (.jsonl / .md)
├── web/                # Next.js statik arayüz (sohbet, /pano, /degisiklikler, /yontem, /gelistirici)
├── desktop/            # Tauri 2 masaüstü (EXE) ve mobil (Android APK) kabuğu
├── deploy/oracle/      # Yayın: compose (Qdrant + API + Caddy + günlük güncelleme), kurulum betiği
└── docs/               # Mimari şema, ekran görüntüleri, demo senaryosu
```

## Neden Böyle?

- **İki kanallı arama:** Mevzuat (`5` aday) ve KVKK kararları (en fazla `3` karardan `2`'şer parça) ayrı aranır; tek havuz kısa karar parçalarını öne çıkarıp mevzuat başarısını `9/9`'dan `8/9`'a düşürmüştür (`KARARLAR.md`).
- **Hibrit parça boyu:** Madde `<= 1500` karakterse tek parça, büyükse fıkra bazında bölünür; uzun bent listeleri (`> 3000` karakter) gruplanır (`KARARLAR.md`).
- **Eşik kalibrasyonu ayrı sette:** Eşik (`0,637`) `56` soruluk testten ayrı `30` soruluk `eval/calibration.jsonl` setinde seçildi; veri sızıntısı önlenir (`KARARLAR.md`).
- **Fark JSON'unun önceden hesaplanması:** `src/update/diff.py` değişiklik anında kelime farkını `data/store/farklar/<fark_id>.json` olarak yazar; canlıda ham sürüm dosyası tutulmaz (`KARARLAR.md`).
- **Çekirdeği LangChain'e taşımama:** Hazır hibrit + RRF + atıf doğrulama hattı gerileme riski yaratmamak için sade bırakıldı; LangGraph yalnızca ajan modunda kullanılır (`KARARLAR.md`).
- **OpenTelemetry + Jaeger seçimi:** Langfuse harici hesap veya ağır yan servisler gerektirdiğinden satıcı bağımsız OTel + `logs/izler.jsonl` seçildi (`KARARLAR.md`).

## Lisans

Kod [MIT lisansı](LICENSE) ile yayımlanır. Bu lisans yalnız bu depodaki kodu kapsar: mevzuat metinleri ve KVKK kararları kendi kaynaklarına aittir, geniş katman verisi (`hasankursun/turkish-legislation-corpus`) **CC-BY-4.0** ile lisanslıdır ve atıf gerektirir (bkz. [Veri kaynakları](#veri-kaynakları)). Sistem hukuki tavsiye vermez.
