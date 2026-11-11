# Kararlar

Format: `- YYYY-MM-DD [ajan] karar — gerekçe`

- 2026-11-11 [claude] Kaynak: mevzuat.gov.tr PDF'leri (1.5.6698.pdf, 1.5.4857.pdf) kullanıcı tarafından elle indirildi — siteye ajan ortamından erişim 403; elle indirme tekrarlanabilir ve tek seferlik.
- 2026-11-11 [claude] PDF ayrıştırma pdfplumber ile, karakter boyutu >= 11.5 pt filtresiyle — gövde 12 pt, dipnot 11 pt, dipnot işareti 7-8 pt; tek filtre dipnotları ve metne yapışan işaretleri ("md.)40") birlikte temizliyor.
- 2026-11-11 [claude] Paragraf sınırı girintiden (x0 ~106 pt = paragraf başı, ~71 pt = devam satırı); başlık = girintili ve tamamen kalın satır. Sol kenardaki kalın satırlar gövde sayılır (6698 m.30, 4857 m.116-118'de başlık sanılıp kayboluyordu).
- 2026-11-11 [claude] Fıkra no: 6698'de metindeki "(n)" kullanılır; 4857'de fıkralar numarasız olduğu için sıra ile atanır (numara_kaynagi="sira"); bentler (a), I-, II.) ve bent listesini kapatan cümle önceki fıkraya bağlanır. 4857 fıkra numaraları kullanıcı kontrolü gerektirir.
- 2026-11-11 [claude] Mülga ve başka kanuna işlenmiş hükümler atılmaz, bayrakla tutulur (mulga, diger_kanuna_islendi); arama varsayılan olarak filtreler.
- 2026-11-11 [claude] Parçalama modu varsayılan "hibrit": madde <= 1500 karakterse tek parça, değilse fıkra fıkra. "madde" ve "fikra" modları 15 Kas karşılaştırması için de üretilir. embed_text = "kanun, madde (başlık), fıkra" başlığı + metin.
- 2026-11-11 [claude] Kapsam dışı: 6698 (I) sayılı cetvel ve iki kanunun sonundaki değişiklik listeleri. Not: kıdem tazminatı 4857 m.120 ile yürürlükte bırakılan 1475 s. Kanun m.14'te; derlemde yok — değerlendirme setinde "bilmiyorum"/kapsam notu gerektirir.
- 2026-11-11 [claude] Kapsam genişletildi: derin katman (KVKK + iş + İSG ekosistemi, KVKK kararları/rehberleri, eval ile ölçülür) + geniş katman (tüm kanunlar, ölçülmez). Kendini güncelleyen mimari (günlük kontrol, hash ile artımlı upsert, sürümleme, eval regresyonu). Mahkeme kararları kapsam dışı.
- 2026-11-11 [claude] Derin katman metinleri mevzuat.gov.tr'den alınır (KVKK Mart 2024 değişikliği nedeniyle HF corpus'una güvenilmez).
- 2026-11-11 [claude] Dipnotlar atılmıyor, maddeye `dipnotlar` alanı olarak bağlanıyor (değişiklik geçmişi soruları için); embed_text'e girmez. İşaret 7.5-9.5 pt, dipnot numarası <7.5 pt, dipnot metni 11 pt italik. Bitişik işaretler ("4041") belge sırasına göre ardışık sayılara bölünür; 6698'de 8/8, 4857'de 42/42 dipnot bağlandı.
- 2026-11-11 [claude] Çok belgeli yapı: belge bilgisi configs/sources.json'dan (belge_id, belge_tur, belge_no, belge_adi, kisa_ad, dayanak). Alan adları kanun_no/kanun_adi -> belge_no/belge_adi. Kanun atfı "6698 s. KVKK m. 5/2", yönetmelik/tebliğ atfı "Yıllık Ücretli İzin Yön. m. 9".
- 2026-11-11 [claude] 1475 s. Kanun tamamen alınır; `yururlukte_maddeler: ["14"]` dışındaki maddeler mülga işaretlenir (4857 m.120 yalnızca m.14'ü yürürlükte bıraktı).
- 2026-11-11 [claude] İki PDF biçimi var: mevzuat.gov.tr "MevzuatMetin" Word PDF'i (kanunlar, yurt dışı aktarım yön.) ve "GeneratePdf" HTML çıktısı (diğer yönetmelik/tebliğler; dipnotsuz, değişiklik notları metin içinde). Sayfa düzeni sabit değil, belgeden ölçülüyor (measure_layout: en sık punto = gövde; kenar ve paragraf girintisi satır x0 dağılımından).
- 2026-11-11 [claude] Kalın yazı tespiti "Bold" veya Türkçe "Kalın" yazı tipi adıyla (Fazla Çalışma Yön. PDF'inde font adı "TimesNewRomanKal?n"; ilk denemede 0 madde çıktı).
- 2026-11-11 [claude] ÇSGB'den indirilen Çalışma Süreleri ve Fazla Çalışma yönetmelikleri GeneratePdf sürümleriyle metin olarak birebir aynı; data/raw/_kopya'ya taşındı, okunmuyor. GeneratePdf dosyaları anlamlı adlarla yeniden adlandırıldı.
- 2026-11-11 [claude] 1475'te mülga maddeler aralık olarak yazılı ("Madde 1-13/E- (Mülga...)"); her aralık tek kayıt olarak tutulur, m.14 dışındakiler mülga. "İŞLENEMEYEN HÜKÜMLER" bölümü (başka kanunların 1475'e işlenemeyen maddeleri) kapsam dışı.
