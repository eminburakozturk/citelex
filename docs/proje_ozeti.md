# Citelex — Özgeçmiş, LinkedIn ve Sözlü Sunum Özeti

---

## 1. CV İçin 3 Madde

* **İki katmanlı hibrit RAG ve kod tarafı atıf doğrulama:** Türk iş ve veri koruma mevzuatını (`12` belge, `40` KVKK Kurul kararı; ek `895` kanunluk `44.854` parçalık geniş yedek katman) Qdrant üzerinde `bge-m3` dense + Türkçe `BM25` (`RRF k=60`) ile dizinledi; `30` soruluk ayrı kalibrasyon setinde sabitlenen `0,637` eşiği ve deterministik `[n]` atıf doğrulamasıyla ölçülen tüm çalıştırmalarda **`0` geçersiz atıf**, geniş katman kapalıyken **`6/6` kapsam dışı ret** elde etti (soru seti taslak, hukuki doğrulama bekliyor) (`KARARLAR.md`).
* **LangGraph ajan döngüsü ve bağımsız sadakat değerlendirmesi:** Yalnız eşik altı veya `CEVAP_YOK` durumlarında soruyu mevzuat terimleriyle yeniden yazan `LangGraph` ajanıyla (`deepseek-v4.1-flash`) `56` soruluk değerlendirmede doğruluğu **`%80`'den (`40/50`) `%88`'e (`44/50`)**, GPU `reranker` ile **`%90`'a (`45/50`)** çıkardı; `anthropic/claude-haiku-5.5` hakemiyle iddia düzeyinde **`%94` (`46/49`) tam destekli sadakat** ölçtü ve `10` kararlık elle kontrolde `9` uyum doğruladı (`KARARLAR.md`).
* **Sürüm farkı takibi, gözlemlenebilirlik ve çoklu istemci:** Ayrıştırılmış içerik hash'i ile SQLite sürüm deposunda kelime düzeyinde madde/bölüm farkı (`/degisiklikler`), OpenTelemetry + Jaeger izleme (`src/trace.py`), `stdio` MCP sunucusu (`src/mcp_server.py`), GitHub Actions bellek içi `BM25` arama kapısı ve `Next.js` statik çıktısını paylaşan `Tauri 2` masaüstü (`Windows EXE 8,7 MB`) ve mobil (`Android APK 10,7 MB`) istemcileri geliştirdi (`KARARLAR.md`).

---

## 2. LinkedIn Proje Açıklaması

### Türkçe (~120 kelime)

**Citelex — Türk Mevzuatı için Kaynak Gösteren ve Kendini Güncelleyen RAG Sistemi**

Citelex; Türk iş hukuku, İSG ve kişisel verilerin korunması mevzuatı (`52` çekirdek belge) ile gerektiğinde devreye giren `895` kanunluk (`44.854` parça) geniş katman üzerinde madde ve fıkra düzeyinde kaynak gösteren bir soru-cevap sistemidir. Qdrant'ta `bge-m3` yoğun vektör ve Türkçe `BM25` seyrek aramayı (`RRF`) birleştirir; `30` soruluk ayrı kalibrasyon setinde seçilen `0,637` eşiği yetmediğinde `LangGraph` ajanı soruyu hukuk terimleriyle yeniden yazarak tekrar arar. Doğrulanmamış her `[n]` atfı elenir ve kanıt yoksa sistem `"bilmiyorum"` der.

`56` soruluk değerlendirmede ajan modu doğruluğu `%80`'den `%88`'e (reranker ile `%90`), `claude-haiku-5.5` hakemiyle ölçülen tam destekli sadakati `%94`'e taşıdı; geçersiz atıf `0` kaldı. SQLite sürüm deposu kaynaklardaki kelime farklarını çıkarır; `OpenTelemetry + Jaeger`, `MCP` sunucusu ve `Next.js` / `Tauri 2` istemcileriyle tek mimaride paketlenmiştir.

### English (~120 words)

**Citelex — Citation-Grounded, Self-Updating RAG for Turkish Legislation**

Citelex is a citation-grounded legal RAG system over Turkish labor, occupational safety, and data-protection law (`52` core documents), backed by an `895`-statute (`44,854`-chunk) broad fallback index. It indexes articles and paragraphs in Qdrant using `bge-m3` dense vectors and Turkish `BM25` sparse search (`RRF`). When a `0.637` threshold (calibrated on a separate `30`-question set) or evidence check fails, a `LangGraph` agent rewrites the query once using statutory terminology, while post-generation verification strips invalid `[n]` citations or abstains.

On a `56`-question evaluation, agent mode improved accuracy from `80%` (`40/50`) to `88%` (`44/50`, `90%` with GPU reranking), achieving `94%` (`46/49`) fully supported faithfulness via an external `claude-haiku-5.5` judge and `0` invalid citations. Includes SQLite version diffs, OpenTelemetry + Jaeger tracing, an `MCP` server, and `Next.js` / `Tauri 2` clients.

---

## 3. 30 Saniyelik Sözlü Anlatım

> "Citelex, Türk mevzuatı için geliştirilmiş, her cümlesini madde atfıyla doğrulayan ve kanıt yetmediğinde 'bilmiyorum' diyebilen bir RAG sistemi. Qdrant'ta `bge-m3` ve Türkçe `BM25` ile hibrit arama yapıyor; `30` soruluk ayrı sette seçilen `0,637` eşiğinin altında kalırsa `LangGraph` ajanı soruyu hukuk terimleriyle bir kez yeniden yazıyor. `56` soruluk ölçümde ajan doğruluğu yüzde `80`'den `88`'e, geçersiz atfı `0`'a indirdi; bağımsız hakemle yüzde `94` tam destekli sadakat ölçüldü. Kaynak değişikliklerini sürümleyip kelime farkı çıkarıyor ve OpenTelemetry ile izlenebiliyor."
