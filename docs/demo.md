# Citelex — 5 Dakikalık Mülakat Demosu

> **Ön hazırlık:** `docker compose --profile izleme up -d` ile Qdrant (`6333`), API + statik arayüz (`http://127.0.0.1:8000/`) ve Jaeger (`http://127.0.0.1:16686/`) açık olmalı. Her adımın altında canlı API/LLM kotası yanıt vermezse kullanılacak yedek plan yer alır.

---

## Adım 1 — Normal soru ve kaynak paneli (~45 sn)

* **Ne yapılır:** Ana sayfada (`http://127.0.0.1:8000/`) `"Yıllık izin kaç gündür?"` sorusu gönderilir; yanıt geldikten sonra metin içindeki `[1]` atıf düğmesine tıklanır.
* **Ne görünmeli:** Süreleri kıdem basamaklarıyla (14 / 20 / 26 gün) veren cevap, sağda açılan kaynak panelinde `4857 s. İş Kanunu m. 53` tam metni, değişiklik dipnotları, son kontrol tarihi ve resmî kaynak bağlantısı.
* **Tasarım kararı:** Mevzuat kanalı fıkra düzeyinde aranıp bağlamda tam maddeye genişletilir (`> 3000` karakterlik maddelerde eşleşen fıkra `±1`); KVKK kararlarında ise "olgudan bul, hükümden cevapla" kuralıyla veri sorumlusunun savunması bağlama sokulmaz (`KARARLAR.md`).
* **Yedek plan (API/kota yoksa):** [01_cevap.png](ekran/01_cevap.png) görselini aç ve madde genişletme ile atıf numarası eşlemesinin kod tarafından yapıldığını anlat.

---

## Adım 2 — Kapsam dışı ret / eşik kapısı (~35 sn)

* **Ne yapılır:** `"Yarın İstanbul'da hava nasıl olacak?"` sorusu sorulur.
* **Ne görünmeli:** `"Bu soruya elimdeki kaynaklarla cevap veremiyorum."` kutusu, gerekçesi ve (ajan açıkken 2. deneme notu: *"Soru yeniden yazılıp tekrar arandı; yine yeterli kaynak bulunamadı."*).
* **Tasarım kararı:** `30` soruluk ayrı kalibrasyon setinde incelenen eşikte, yanlış atıflı kendinden emin hataları (`0,574` adayında görülenler) önlemek için tutucu `0,637` dense top-1 eşiği seçilmiştir (`KARARLAR.md`).
* **Yedek plan:** [03_bilmiyorum.png](ekran/03_bilmiyorum.png) görselini göster.

---

## Adım 3 — Ajanın kurtardığı kısa/genel soru (~45 sn)

* **Ne yapılır:** `"İşveren çalışanın parmak izini alabilir mi?"` (veya `"İş güvencesi hükümlerinden yararlanmak için işyerinde en az kaç işçi çalışıyor olmalı?"`) sorusu sorulur; yanıtın altındaki katlanabilir ajan notu açılır.
* **Ne görünmeli:** `"Soru yeniden yazılarak tekrar arandı (2. deneme)"` özeti ve ilk aramada eşik altında kalan soruyu mevzuat terimleriyle (ör. `biyometrik veri`) yeniden aratan sorgu.
* **Tasarım kararı:** Yalnız eşik altı veya `CEVAP_YOK` durumunda devreye giren LangGraph ajanı (`≤ 1` yeniden yazma), `0,637` eşiğini gevşetmeden `deepseek-v4.1-flash`'ta tek adımlı `%80` (`40/50`) doğruluğu `%88`'e (`44/50`), yanlış `"bilmiyorum"` sayısını `7`'den `1`'e düşürdü (`KARARLAR.md`).
* **Yedek plan:** Canlı yanıt gelmezse `/pano` üzerindeki **Yapılandırma karşılaştırması** tablosundan tek adım vs ajan satırlarını göster.

---

## Adım 4 — Geniş katman rozeti (~40 sn)

* **Ne yapılır:** 5. örnek soruya tıklanır: *"Kira sözleşmesinde kiracıdan alınan güvence (depozito) en fazla ne kadar olabilir?"*.
* **Ne görünmeli:** Cevabın üstünde `"Geniş katman · doğruluğu ölçülmedi"` rozeti, altında açık uyarı metni ve `[1]` kaynağı olarak `6098 s. TÜRK BORÇLAR KANUNU m. 342`.
* **Tasarım kararı:** Derin katman `0,637` eşiğini geçemezse veya geniş katman derin katmanı `0,05`'ten fazla geçerse (`GENIS_FARK=0,05`; `eval/calibration.jsonl`'da max derin farkı `+0,021`) `895` kanunluk (`44.843` parça) `citelex_genis` indeksi seçilir; doğruluğu tam eval ile ölçülmediği için yanıtlar rozet ve resmî metin uyarısıyla döner (`KARARLAR.md`).
* **Yedek plan:** [02_genis.png](ekran/02_genis.png) görselini göster; kalan sınır olarak `g02`'nin (`0,629`) eşik altında kaldığına ve `g08`'in (`TCK m.141`) ilk `5`'te çıkmadığına değin.

---

## Adım 5 — Sürüm takibi ve madde/bölüm farkı (`/degisiklikler`, ~40 sn)

* **Ne yapılır:** Üst menüden **Son değişiklikler** (`/degisiklikler/`) açılır; kayıtlı fark kartına ve **Satır içi fark** / **Eski / Yeni metin** geçişine tıklanır.
* **Ne görünmeli:** **Test kaydı** rozetli iki kart — gerçek bir Kurul kararı değişikliği değil, güncelleme hattını denemek için yapılan sahte değişiklik (bunu açıkça söyle). KVKK `2023/2007` kararındaki `#52 → #12` sürüm geçişi ve hüküm bölümünde satır içi kelime farkı (`125.000 TL` ↔ `175.000 TL`).
* **Tasarım kararı:** `GeneratePdf` çıktıları her indirmede gömülü `CreationDate` yüzünden farklı bayt ürettiğinden sürüm karşılaştırması ayrıştırılmış içerik hash'iyle yapılır; fark JSON'u canlıda ham dosya tutmamak için güncelleme anında önceden hesaplanır (`KARARLAR.md`).
* **Yedek plan:** [05_degisiklik.png](ekran/05_degisiklik.png) görselini veya `/degisiklikler` sayfasının `data/store/farklar` örnek modunu göster.

---

## Adım 6 — Değerlendirme panosu ve sadakat (`/pano`, ~45 sn)

* **Ne yapılır:** **Değerlendirme panosu** (`/pano/`) açılır; **Model karşılaştırması**, **Yapılandırma karşılaştırması** ve **Geniş katman** bölümleri gösterilir.
* **Ne görünmeli:** Üç tek-adımlı modelin anahtar kelime doğruluğu (`%80` / `%78` / `%78`), buna karşın `tam_destekli` sadakat farkı (`%95` vs `%83` vs `%62`), `ajan + reranker` (`45/50`, `%90`) ve `TASLAK` geniş katman özeti (`R@1 8/15`, `R@5 14/15`).
* **Tasarım kararı:** Geçerli atıf ve anahtar kelime eşleşmesi anlamsal sadakati kanıtlamadığı için üç farklı model ailesi dışından `claude-haiku-5.5` hakemiyle iddia bazlı `tam_destekli` ölçütü eklenmiştir (`KARARLAR.md`).
* **Yedek plan:** `/pano` tamamen statik `web/public/pano.json` dosyasından beslendiği için LLM/API kapalıyken de açılır; alternatif olarak [04_pano.png](ekran/04_pano.png) gösterilir.

---

## Adım 7 — İzlenebilirlik (`Jaeger`, ~30 sn)

* **Ne yapılır:** `http://127.0.0.1:16686/` adresinde `citelex-api` servisi seçilip **Find Traces** ile son sorgunun izi açılır.
* **Ne görünmeli:** `POST /sor` altında `sor` span'i (ajan kapalıyken `sor → arama, llm` alt span'leri), `citelex.ajan`, `citelex.ajan_deneme`, `citelex.atif`, `citelex.maliyet_usd` ve `gen_ai.request.model` / `gen_ai.usage.*` öznitelikleri.
* **Tasarım kararı:** Harici hesap ve Postgres/ClickHouse/Redis kurulumu gerektiren Langfuse yerine satıcı bağımsız OpenTelemetry (`src/trace.py`) ve tek satırlık `logs/izler.jsonl` özeti tercih edilmiştir (`KARARLAR.md`).
* **Yedek plan:** [07_jaeger.png](ekran/07_jaeger.png) görselini ve `logs/izler.jsonl`'nin son satırlarını göster.

---

## Sık Sorulan Mülakat Soruları

### 1. Neden çekirdeği LangChain'e taşımadın?
Çalışan ve tek adımlı eval setinde ölçülmüş hibrit arama (`bge-m3` + Türkçe `BM25`, `RRF k=60`) ve kod tarafı atıf doğrulama hattını soyutlama katmanına taşımak kalite kazandırmayıp gerileme riski yaratıyordu. Yalnızca "bilmiyorum" durumunda soruyu yeniden yazıp ikinci kez arayan döngüye ihtiyaç duyulduğunda `LangGraph` eklendi ve tek adımlı hatla aynı `56` soruluk sette yan yana ölçüldü (`KARARLAR.md`).

### 2. LLM hakemini nasıl doğruladın?
İlk denenen `qwen3.7-flash` hakemi kendi gerekçesiyle çelişip yanlış "desteksiz" etiketleri verdiği için model seçimi `anthropic/claude-haiku-5.5`'e alındı (`eval` modellerinden farklı aile, kendini kayırma yok). Hakem çıktısı üzerinde `10` kararlık elle kontrol yapıldı: hakemin "desteksiz" dediği `5` iddiadan `4`'ü doğru çıktı, `1` hatanın kaynağı `6000` karakter kesme sınırı olduğu görülüp `15000` karaktere çıkarıldı; rastgele `5` "sadık" cevapta kaçırılan iddia bulunmadı ve hakemin kararsız kaldığı `desteksiz`/`kismen` ayrımı yerine `tam_destekli` (`kismen=0` ve `desteksiz=0`) asıl ölçüt seçildi (`KARARLAR.md`).

### 3. Eşiği nasıl seçtin, veri sızıntısını nasıl önledin?
İlk kalibrasyon eval setiyle çakışmayan `10`, ardından `30` soruluk ayrı `eval/calibration.jsonl` setinde "kapsam içi en düşük skor − 0,02" kuralıyla yapıldı (`0,637` ve `0,574` adayları). `0,574` eval üzerinde daha yüksek ham doğru (`34/46`) üretse de geçerli atıflı yanlış cevapları (`e02`, `e37`, `d03`) artırdığı için hukuk alanında daha güvenli olan `0,637` korundu. Bu iki aday seçimi eval sonucu görülerek yapıldığı için yöntemsel sınırlılık olarak belgelendi; kalibrasyon soruları hiçbir zaman test setine dahil edilmedi (`KARARLAR.md`).

### 4. Ajan modu neden %80'i %88'e çıkardı?
Tek adımda `deepseek-v4.1-flash` (`40/50`) ve `deepseek + reranker` (`40/50`) aynı `7` yanlış `"bilmiyorum"` hatasını veriyordu ve bunların `7/7`'si `arama_esigi` katmanından dönüyordu; yani darboğaz sıralama değil, kısa kullanıcı sorusunun mevzuat terminolojisiyle eşleşememesiydi. `LangGraph` ajanı yalnızca eşik altı veya `CEVAP_YOK` durumunda soruyu Türk mevzuatı terimleriyle yeniden yazıp en fazla bir kez daha aradığı için bağlam kaçan `5` soruyu (`e02`, `e35`, `e39`, `e42`, `e49`) kurtardı ve yanlış reddi `7`'den `1`'e indirirken kapsam dışı reddi `6/6`'da korudu (`KARARLAR.md`).

### 5. Reranker neden yayında kapalı?
`bge-reranker-v2-m3` GPU (`fp16`) üzerinde `30` adayı sorgu başına `0,7–1,5 sn`'de sıralayıp mevzuat `R@1`'i `44/51`'den `48/51`'e çıkarsa da (`results/rerank_compare.md`), `16` çekirdekli CPU (`fp32`) ölçümünde sorgu başına `43,0 / 118,9 / 42,9 sn` sürdü. Oracle Cloud Always Free (`ARM` CPU) ve Docker CPU ortamında kullanıcı bekleme süresini patlattığı ve tek başına uçtan uca eval'de `40/50`'yi değiştirmediği için yayında `CITELEX_RERANK=0` ile kapalı tutulur; yerel GPU'da ajanla birlikte (`45/50`, `%90`) açılabilir (`KARARLAR.md`).

### 6. Geniş katmanı nasıl ölçtün ve yönlendirmede kalan sınır ne?
Derin katman (`12` mevzuat, `40` karar) dışındaki `895` kanunluk (`44.843` parça) geniş katman, ana `56` soruluk açık eval'de test edildiğinde kapsam içi skor değişmedi (`45/50`), ancak kapsam dışı sayılan `d03` (`7036` s. İş Mahkemeleri Kanunu m.3) doğru atıfla yanıtlandığı için ret `6/6`'dan `5/6`'ya düştü (`KARARLAR.md`). İlk sürümde yalnız derin katman `0,637` altında kaldığında genişe gidildiği için `g13` (devlet memuru analık izni) derin katmandaki İş Kanunu m.74 (`0,717`) tarafından gölgeleniyordu; kalibrasyon setinde (`18` kapsam içi soru) geniş katmanın derin sorularındaki en büyük üstünlüğü `+0,021` (`c11`) ölçülerek `2` kat payla `GENIS_FARK=0,05` kuralı getirildi (geniş katman derini `0,05`'ten fazla geçerse seçilir). Bu kural derin eval yönlendirmesini değiştirmezken `15+3` `TASLAK` geniş sette (`results/genis_check.md`) yönlendirmeyi `14/15`'e, bağlamda beklenen maddeyi `13/15`'e çıkardı (doğrudan geniş `R@1 8/15` — RRF deterministik yapılmadan önce 8 ile 9 arasında oynuyordu, `R@5 14/15`, eşikte ret `3/3`). Kalan sınırlar: `g02` (anlaşmalı boşanma) `0,629` skoruyla eşiğin hemen altında kalıp reddediliyor, `g08` (`TCK m.141`) ilk `5`'te gelmiyor. Ayrıca `g13` bu kuralı bulduran örnek olduğu için geniş taslak seti bu değişiklik açısından bağımsız değildir (`KARARLAR.md`).

### 7. Güncelleme hattı nasıl çalışır?
`src/update/run.py` kaynakları (`mevzuat.gov.tr`, `kvkk.gov.tr`, Resmî Gazete fihristi) nazik istemciyle (`robots.txt`, `2 sn` bekleme) indirir ve `GeneratePdf` dosyalarında CreationDate farkına düşmemek için ham bayt yerine ayrıştırılmış metnin hash'ini SQLite deposuyla karşılaştırır. Değişiklik varsa eski sürüm silinmeden `eski` işaretlenir, kelime düzeyinde fark JSON'u (`data/store/farklar/<fark_id>.json`) üretilir ve Qdrant'a yalnız `chunk_id → content_hash` farkı olan parçalar yeniden yazılıp silinir (sabit `BM25 avgdl` + embedding önbelleği). Ardından otomatik arama regresyon kontrolü koşturularak sonuç `logs/updates.jsonl`'ye yazılır (`KARARLAR.md`).

### 8. Neyi farklı yapardın?
İlk olarak, eşik ve fark kalibrasyonunu eval sonucuna bakarak seçmek veya tek bir örnek (`g13`) üzerine kural kurmak yerine, başlangıçta `eval/calibration.jsonl` içinde "yakın kapsam dışı soruların en az %X'ini kesen en düşük eşik" ve kalibrasyon-içi katman yönlendirme kuralı tanımlardım (`KARARLAR.md`). İkinci olarak, mevzuat PDF değişiklik yolunu da sahte karar değişikliği testi gibi uçtan uca bir regresyon testiyle doğrulatırdım. Üçüncü olarak, geniş katmandaki `g02` (`0,629`) ve `g08` (`TCK m.141`) kaçırmaları için kanun adı / kurum ipuçlarını hibrit skora daha iyi yansıtan ayrı bir geri getirme analizi yapardım.

### 9. Bulduğun en ilginç hata neydi?
İki katmanı ayrı ayrı ölçmek yetmedi; birlikte çalışınca etkileştiler. Yayında çalışacak yapılandırmayı (ajan + geniş katman, reranker kapalı) ölçtüğümde `43/50` çıktı, geniş katmansız ajandan (`44/50`) bir eksik. `e35` derin katmandaki bir yönetmelikle cevaplanabilen bir soruydu; derin katman eşiği ilk aramada geçilemiyordu. Önceden ajan bu durumda soruyu yeniden yazıp doğru yönetmeliği buluyordu, ama artık geniş katman ilgisiz bir kanunla (7315 s.) eşiği geçip araya giriyor ve ajan hiç devreye girmiyordu. Düzeltme bir eşik ayarı değil, öncelik sırasıydı: ajan önce derin katmanda yeniden yazıp arar, geniş katmana en son düşer. Sonuç `44/50`, sadakat `%94`. Not: `e35` hatayı bulduran soru olduğu için bu artış bağımsız bir ölçüm değildir (`KARARLAR.md`).

### 10. Yapay zekâ araçlarını nasıl kullandın?
Proje yapay zekâ kodlama ajanlarıyla (Claude Code ana geliştirici, Antigravity destek) geliştirildi; benim rolüm hedefleri ve kapsamı belirlemek, ürün kararlarını vermek (ör. "bilmiyorum" eşiğinin yönü, model zinciri, barındırma) ve çıktıları denetletmekti. Ajanların işleri ayrıca denetlendi: bu denetimde örneğin sahte bir test değişikliğinin arayüzde gerçek bir Kurul kararı değişikliği gibi göründüğü ve CI'da bir bağımlılığın eksik olduğu yakalandı. Bütün kararlar ve gerekçeleri `KARARLAR.md`'de tarihli olarak duruyor.

