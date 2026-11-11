# Arama sağlık kontrolü (hibrit, ilk 5)

Beklenen maddeler ajan tarafından ayrıştırılmış metinden doğrulandı (kanit alanı); bağımsız insan doğrulaması değil. 10 soru: sağlık kontrolü, karşılaştırma değil. Hücre: beklenen maddenin sırası (— = ilk k'da yok).

| # | Soru | Beklenen | dense | bm25 | hybrid | Hibrit ilk 3 |
|---|---|---|---|---|---|---|
| r01 | Açık rıza alınmadan kişisel veriler hangi şartlarda işlenebilir? | kvkk:5 | 1 | 4 | 1 | 6698 s. KVKK m. 5; 6698 s. KVKK m. 8; 6698 s. KVKK m. 3 |
| r02 | Sağlık ve cinsel hayata ilişkin veriler hangi durumlarda işlenebilir? | kvkk:6 | 1 | 1 | 1 | 6698 s. KVKK m. 6/3; 6698 s. KVKK m. 6/1; 6698 s. KVKK m. 5 |
| r03 | Veri sorumlusu ilgili kişinin başvurusunu en geç kaç gün içinde sonuçlandırmalı? | kvkk:13, basvuru-teblig:6 | 1 | 2 | 1 | Başvuru Tebliği m. 6; 6698 s. KVKK m. 13; Silme-İmha Yön. m. 12 |
| r04 | İş sözleşmesine konulan deneme süresi en fazla ne kadar olabilir? | is-kanunu:15 | 1 | 1 | 1 | 4857 s. İş Kanunu m. 15; 4857 s. İş Kanunu m. 53; Yıllık Ücretli İzin Yön. m. 9 |
| r05 | Fazla mesai ücreti normal ücrete göre yüzde kaç zamlı ödenir? | is-kanunu:41, fazla-calisma-yon:4 | 1 | 1 | 1 | Fazla Çalışma Yön. m. 4/1; 4857 s. İş Kanunu m. 41/2; Fazla Çalışma Yön. m. 4/2 |
| r06 | Beş yıldan fazla çalışmış bir işçinin yıllık izni kaç gündür? | is-kanunu:53, yillik-izin-yon:9 | 1 | 1 | 1 | Yıllık Ücretli İzin Yön. m. 9; 4857 s. İş Kanunu m. 53; 4857 s. İş Kanunu m. 55 |
| r07 | Haftalık çalışma süresi en çok kaç saattir? | is-kanunu:63, calisma-sureleri-yon:4 | 1 | 1 | 1 | 4857 s. İş Kanunu m. 63; Çalışma Süreleri Yön. m. 4; Çalışma Süreleri Yön. m. 5 |
| r08 | Kıdem tazminatına hak kazanmak için işyerinde en az ne kadar çalışmak gerekir? | is-kanunu-1475:14 | 1 | 2 | 2 | 4857 s. İş Kanunu m. 112/3; 1475 s. İş Kanunu m. 14/2; 4857 s. İş Kanunu m. 112/2 |
| r09 | Saklama ve imha politikası olan şirket periyodik imhayı en geç kaç ayda bir yapmalı? | imha-yon:11 | 1 | 2 | 2 | Silme-İmha Yön. m. 6; Silme-İmha Yön. m. 11; Silme-İmha Yön. m. 5 |
| r10 | 2026 yılında net asgari ücret ne kadardır? | kapsam dışı | top1 0.526: 4857 s. İş Kanunu m. 39 | top1 8.241: 4857 s. İş Kanunu m. 39 | top1 0.033: 4857 s. İş Kanunu m. 39 | 4857 s. İş Kanunu m. 39; 4857 s. İş Kanunu geç. m. 3; 4857 s. İş Kanunu m. 32/2 |

İlk 5'te isabet (9 kapsam içi soru): dense 9/9, bm25 9/9, hybrid 9/9
