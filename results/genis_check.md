# Geniş katman arama ölçümü (taslak set, LLM yok)

Eşik 0.637. Soru: 15 kapsam içi + 3 kapsam dışı (eval/genis_sorular.jsonl, TASLAK).

| Ölçüt | Değer |
|---|---|
| Geniş katmana yönlendirildi | 14/15 |
| Beklenen madde üretim bağlamında | 13/15 |
| Doğrudan geniş arama R@1 | 9/15 |
| Doğrudan geniş arama R@5 | 14/15 |
| Kapsam dışı: hiçbir kanala gitmedi (eşikte ret) | 3/3 |

| # | Soru | Beklenen | Kanal | Bağlamda | Sıra | İlk 3 |
|---|---|---|---|---|---|---|
| g01 | Konut kira artışlarında yenilenen kira döneminde yasal üst sınır nasıl | kanun-6098:344 | genis (0.689) | ✓ | 2 | kanun-6098:Geçici 2; kanun-6098:344; kanun-6098:Geçici 1 |
| g02 | Anlaşmalı boşanma davası açabilmek için evliliğin en az ne kadar sürmü | kanun-4721:166 | mevzuat (0.629) | ✗ | 1 | kanun-4721:166; kanun-4721:164; kanun-4721:161 |
| g03 | Tacirler arasında temerrüde düşürme veya sözleşmeden dönme ihtarları h | kanun-6102:18 | genis (0.648) | ✓ | 2 | kanun-6102:1530; kanun-6102:18; kanun-6098:235 |
| g04 | Mal teslim edildikten veya hizmet yapıldıktan sonra fatura en geç kaç  | kanun-213:231 | genis (0.735) | ✓ | 1 | kanun-213:231; kanun-5510:97; kanun-6102:1530 |
| g05 | Hukuk mahkemesinin kararına karşı istinaf yoluna başvuru süresi kaç ha | kanun-6100:345 | genis (0.761) | ✓ | 3 | kanun-2004:363; kanun-6100:348; kanun-6100:345 |
| g06 | İlamsız icra takibinde ödeme emrini alan borçlu kaç gün içinde ve nere | kanun-2004:62 | genis (0.770) | ✓ | 2 | kanun-7155:7; kanun-2004:62; kanun-2004:172 |
| g07 | İnternetten yapılan mesafeli satışlarda tüketici gerekçe göstermeden k | kanun-6502:48 | genis (0.715) | ✓ | 2 | kanun-6502:49; kanun-6502:48; kanun-6502:47/A |
| g08 | Basit hırsızlık suçunun kanunda öngörülen hapis cezası alt ve üst sını | kanun-5237:141 | genis (0.641) | ✗ | — | kanun-5237:144; kanun-5237:142; kanun-5237:282 |
| g09 | Trafik kontrolünde alkol ölçümü için teknik cihaza üflemeye izin verme | kanun-2918:48 | genis (0.683) | ✓ | 1 | kanun-2918:48; kanun-2918:51; kanun-2918:72 |
| g10 | İşveren yeni işe alacağı işçinin sigortalı işe giriş bildirgesini SGK' | kanun-5510:8 | genis (0.747) | ✓ | 1 | kanun-5510:8; kanun-5510:11; kanun-4447:48 |
| g11 | Kamu ihalesi sürecinde hukuka aykırılık iddiasıyla ihaleyi yapan idare | kanun-4734:55 | genis (0.742) | ✓ | 1 | kanun-4734:55; kanun-4734:54; kanun-4734:56 |
| g12 | Bireysel işlenen suçlarda gözaltı süresi en fazla ne kadar sürebilir? | kanun-5271:91 | genis (0.664) | ✓ | 1 | kanun-5271:91; kanun-3713:Geçici 19; kanun-7074:Geçici 1 |
| g13 | Kadın devlet memuruna doğumdan önce ve sonra toplam kaç hafta analık i | kanun-657:104 | genis (0.813) | ✓ | 1 | kanun-657:104; kanun-2692:Ek 11; kanun-657:108 |
| g14 | Bir takvim yılına ait yıllık gelir vergisi beyannamesi ne zamana kadar | kanun-193:92 | genis (0.779) | ✓ | 1 | kanun-193:92; kanun-193:84; kanun-1319:47 |
| g15 | Özel kanunda ayrı süre öngörülmemişse idare mahkemesi ve vergi mahkeme | kanun-2577:7 | genis (0.751) | ✓ | 1 | kanun-2577:7; kanun-2577:10; kanun-213:Ek 15 |
| g16 | 2026 yılı için geçerli net asgari ücret tutarı kaç TL olarak belirlenm | kapsam dışı | mevzuat (0.562) | ✗ | — | kanun-193:Geçici 86; kanun-193:Geçici 87; kanun-193:31 |
| g17 | Türkiye'de 10 yıl kıdemli bir yazılım mühendisinin ortalama piyasa maa | kapsam dışı | mevzuat (0.528) | ✗ | — | kanun-926:Ek Geçici 23; kanun-2879:4; kanun-926:36 |
| g18 | Ankara'daki ehliyet direksiyon sınavı randevu takvimi hangi tarihte aç | kapsam dışı | karar (0.502) | ✗ | — | kanun-2918:Geçici 5; kanun-3224:23; kanun-3213:Geçici 6 |
