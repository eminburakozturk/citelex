[![CI](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml/badge.svg)](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml)

# Citelex — Türk Mevzuatı için Kaynak Gösteren RAG

**Citelex**, Türk iş hukuku ve kişisel verilerin korunması alanındaki temel mevzuatı (12 mevzuat belgesi ve 40 seçili KVKK Kurul kararı; toplam 52 belge) madde ve fıkra düzeyinde dizinleyip her iddiayı doğrudan resmi kaynağa dayandırarak yanıtlayan, kaynak değiştikçe kendini güncelleyebilen ve kanıt yetersiz kaldığında `"bilmiyorum"` diyebilen bir RAG sistemidir.

> **Uyarı:** Bu sistem hukuki tavsiye vermez; yalnızca dizinlenen mevzuat ve kurul kararları üzerinden kaynak göstererek bilgi sunar.

## Mimari

![](docs/mimari.svg)

## Sonuçlar

### Model karşılaştırması (56 soruluk set: 50 kapsam içi, 6 kapsam dışı)

| Model (yapılandırma) | Doğru | Tam destekli sadakat | İddia desteği | Yanlış "bilmiyorum" | Kapsam dışı ret | Medyan süre |
|---|---:|---:|---:|---:|---:|---:|
| `openrouter:deepseek/deepseek-v4.1-flash-1017` (ajan) | 44/50 (%88) | — | — | 1/50 (%2) | 6/6 (%100) | 2,42 sn |
| `openrouter:deepseek/deepseek-v4.1-flash-1017` (reranker) | 40/50 (%80) | — | — | 7/50 (%14) | 6/6 (%100) | 3,66 sn |
| `openrouter:deepseek/deepseek-v4.1-flash-1017` (tek adım) | 40/50 (%80) | 41/43 (%95) | 161/163 (%99) | 7/50 (%14) | 6/6 (%100) | 1,90 sn |
| `openrouter:qwen/qwen3.7-flash` (tek adım) | 39/50 (%78) | 26/42 (%62) | 145/162 (%90) | 8/50 (%16) | 6/6 (%100) | 2,39 sn |
| `openrouter:nvidia/nemotron-3-ultra-550b-a55b:free` (tek adım) | 39/50 (%78) | 35/42 (%83) | 86/93 (%92) | 8/50 (%16) | 6/6 (%100) | 2,43 sn |
| `ollama:qwen2.5:7b` (tek adım) | 33/50 (%66) | — | — | 12/50 (%24) | 6/6 (%100) | 2,86 sn |

*Kaynak: `results/eval_history.jsonl`, `results/eval_*.md` ve `results/sadakat_*__hakem_openrouter_anthropic_claude_haiku_5.5.jsonl`. Tüm çalıştırmalarda geçersiz atıf `0`'dır.*

### Yapılandırma ve reranker karşılaştırması

| Yapılandırma (`deepseek-v4.1-flash-1017`) | Bağlam | Atıf | İçerik | Doğru | Yanlış ret (katman) | Medyan / En uzun |
|---|---:|---:|---:|---:|---|---:|
| Tek adım | 45/50 (%90) | 40/50 (%80) | 42/50 (%84) | 40/50 (%80) | 7/50 (%14) — `arama_esigi: 7` | 1,90 sn / — |
| + Reranker (`bge-reranker-v2-m3`) | 47/50 (%94) | 41/50 (%82) | 42/50 (%84) | 40/50 (%80) | 7/50 (%14) — `arama_esigi: 7` | 3,66 sn / — |
| + Ajan (LangGraph) | 45/50 (%90) | 45/50 (%90) | 47/50 (%94) | 44/50 (%88) | 1/50 (%2) — `arama_esigi: 1` | 2,42 sn / 118,65 sn |

*Kaynak: `results/eval_openrouter_deepseek_deepseek_v4.1_flash_1017.md`, `results/eval_openrouter_deepseek_deepseek_v4.1_flash_1017_rerank.md`, `results/eval_openrouter_deepseek_deepseek_v4.1_flash_1017_ajan.md`.*

| Yöntem (geri getirme) | Alt küme | R@1 | R@3 | R@5 | MRR |
|---|---|---:|---:|---:|---:|
| Hibrit (bge-m3 + BM25, RRF k=60) | Mevzuat (`n=51`) | 43/51 | 48/51 | 48/51 | 0,898 |
| Hibrit + reranker (30 aday) | Mevzuat (`n=51`) | 48/51 | 49/51 | 50/51 | 0,957 |
| Hibrit | KVKK kararı (`n=12`) | 11/12 | 12/12 | 12/12 | 0,958 |
| Hibrit + reranker (30 aday) | KVKK kararı (`n=12`) | 12/12 | 12/12 | 12/12 | 1,000 |

*Kaynak: `results/rerank_compare.md` (rerank süresi GPU fp16'da medyan 0,74 sn/sorgu; canlı CPU sunucuda varsayılan kapalı, `CITELEX_RERANK=1` ile açılır).*

### CI arama kapısı temel değerleri

- **BM25 (bellek içi fixture):** mevzuat `48/51`, KVKK kararı `12/12`
- **Qdrant (hibrit):** mevzuat `48/51`, KVKK kararı `12/12`

*Kaynak: `eval/gate_baseline.json`.*

## Değerlendirme Yöntemi ve Sınırlar

- **Taslak soru seti ve içerik ölçütü:** 56 soruluk değerlendirme setindeki beklenen cevaplar taslaktır (kullanıcı hukuki doğrulaması gerekir); `icerik` ölçütü anlamsal eşdeğerlik yerine anahtar kelime eşleşmesine dayanır (`KARARLAR.md`).
- **Hakem kararlılığı:** LLM hakem (`anthropic/claude-haiku-5.5`) üzerindeki 10 kararlık elle kontrolde 9 uyum görülmüştür; asıl sadakat ölçütü tüm iddiaların desteklendiği `tam_destekli` oranıdır (`kismen == 0 ve desteksiz == 0`) (`KARARLAR.md`).
- **Eşik tercihi:** Kalibrasyon `30` soruluk ayrı sette yapılmış; `0,574` yerine `0,637` eşiği seçilmiştir (`KARARLAR.md`, `results/calibration.md`). Bu tercih uydurma atıflı yanlış cevap riskini azaltırken kısa veya genel kapsam içi sorularda fazladan `"bilmiyorum"` dönmesine yol açabilir (`KARARLAR.md`).
- **Kapsam ve örneklem:** Geniş katmandaki `895` kanun (`32.694` madde) indeks dışı ve değerlendirme dışı tutulur (`results/genis_katman_rapor.md`); mevcut metrikler `56` soruluk küçük örneklem üzerindendir (`KARARLAR.md`).

## Kurulum

### 1. Ortam ve bağımlılıklar

```bash
conda activate citelex
# veya yeni ortam: pip install -r requirements.txt
```

`.env` dosyasını `.env.example` şablonundan oluşturun (değerleri örnekten kendi anahtarlarınızla doldurun):

- `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `OPENROUTER_MODELS`, `OLLAMA_HOST`, `CITELEX_LLM`, `QDRANT_URL`
- Hız sınırı ve proxy/CORS: `CITELEX_RATE_DK`, `CITELEX_RATE_GUN`, `CITELEX_GUNLUK_TOPLAM`, `CITELEX_TRUST_PROXY`, `CITELEX_CORS`

### 2. Altyapı, veri hazırlama ve indeksleme

```bash
docker compose up -d qdrant
python -m src.ingest.parse
python -m src.ingest.chunk --mode hibrit --max-chars 1500
python -m src.ingest.parse_karar
python -m src.index.build --mode hibrit --recreate
python -m src.update.run --init
```

### 3. API, Web arayüzü ve izlenebilirlik

```bash
docker compose up -d api
npm --prefix web run dev
```

Jaeger ile OpenTelemetry izlerini (`http://127.0.0.1:16686`) açmak için:

```bash
docker compose --profile izleme up -d
```

### 4. MCP sunucusu

`src/mcp_server.py` (`mcp` stdio aktarımı) `mevzuat_ara` ve `madde_getir` araçlarını sunar. Örnek `claude_desktop_config.json` ayarı:

```json
{
  "mcpServers": {
    "citelex": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "<REPO_KOKU>"
    }
  }
}
```

## Proje Yapısı

```text
citelex/
├── src/
│   ├── api/            # FastAPI + SSE akışı, hız sınırı, /degisiklikler, /kaynak
│   ├── ingest/         # PDF/HTML ayrıştırma ve hibrit madde/fıkra parçalama
│   ├── index/          # bge-m3 dense + Türkçe BM25 sparse Qdrant indeksi
│   ├── retrieve/       # İki kanallı arama, eşik kapısı, bge-reranker-v2-m3
│   ├── generate/       # OpenRouter/Gemini/Ollama üretimi, atıf doğrulama, LangGraph ajan
│   ├── update/         # Sürüm deposu (SQLite), kelime/madde farkı, erken uyarı
│   ├── tools.py        # API, ajan ve MCP için ortak araç katmanı
│   ├── trace.py        # OpenTelemetry + logs/izler.jsonl
│   └── mcp_server.py   # MCP sunucusu (mevzuat_ara, madde_getir)
├── eval/               # Kalibrasyon, değerlendirme koşucusu, hakem, CI BM25 kapısı
├── scripts/            # Yardımcı analiz ve pano_veri.py betikleri
├── results/            # Eval, sadakat ve rerank çıktıları (.jsonl / .md)
├── web/                # Next.js statik arayüz (sohbet, /pano, /degisiklikler)
└── docs/               # Mimari diyagram (mimari.svg)
```

## Neden Böyle?

- **İki kanallı arama:** Mevzuat (`5` aday) ve KVKK kararları (en fazla `3` karardan `2`'şer parça) ayrı aranır; tek havuz kısa karar parçalarını öne çıkarıp mevzuat başarısını `9/9`'dan `8/9`'a düşürmüştür (`KARARLAR.md`).
- **Hibrit parça boyu:** Madde `<= 1500` karakterse tek parça, büyükse fıkra bazında bölünür; uzun bent listeleri (`> 3000` karakter) ayrıca gruplanarak bağlam bütünlüğü korunur (`KARARLAR.md`).
- **Eşik kalibrasyonu ayrı sette:** Eşik (`0,637`) ana `56` soruluk testten ayrı `30` soruluk `eval/calibration.jsonl` setinde seçildi; veri sızıntısı önlenir ve uydurma atıf yerine `"bilmiyorum"` tercih edilir (`KARARLAR.md`).
- **Fark JSON'unun önceden hesaplanması:** `src/update/diff.py` değişiklik anında kelime farkını `data/store/farklar/<fark_id>.json` olarak yazar; canlıda ham sürüm dosyaları tutulmadığı için ek dosya gerektirmez (`KARARLAR.md`).
- **Çekirdeği LangChain'e taşımama:** Hazır hibrit + RRF + atıf doğrulama hattı gereksiz soyutlama ve gerileme riski yaratmamak için sade bırakıldı; LangGraph yalnızca çok adımlı ajan modunda kullanılır (`KARARLAR.md`).
- **OpenTelemetry + Jaeger seçimi:** Langfuse harici hesap veya Postgres+ClickHouse+Redis yığını gerektirdiğinden satıcı bağımsız OTel + yerel JSONL (`logs/izler.jsonl`) ve isteğe bağlı Jaeger profili tercih edildi (`KARARLAR.md`).
