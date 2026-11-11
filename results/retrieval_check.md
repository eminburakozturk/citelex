# Arama sağlık kontrolü (hibrit, iki kanal: mevzuat ilk 5, karar ilk 3 karar)

Beklenenler ajan tarafından ayrıştırılmış metinden doğrulandı (kanit alanı); bağımsız insan doğrulaması değil. Küçük örneklem: sağlık kontrolü, karşılaştırma değil. Hücre: beklenenin sırası (— = yok).

| # | Kanal | Soru | Beklenen | dense | bm25 | hybrid | Hibrit: ilk sonuçlar |
|---|---|---|---|---|---|---|---|
| r01 | mevzuat | Açık rıza alınmadan kişisel veriler hangi şartlarda işlenebilir? | kvkk:5 | 1 | 4 | 1 | 6698 s. KVKK m. 5; 6698 s. KVKK m. 8; KVKK Kurulu K. 2024/1361 (Kurulun değerlendirmesi/5) |
| r02 | mevzuat | Sağlık ve cinsel hayata ilişkin veriler hangi durumlarda işlenebilir? | kvkk:6 | 1 | 1 | 1 | 6698 s. KVKK m. 6/3; 6698 s. KVKK m. 6/1; KVKK Kurulu K. 2023/787 (Kurulun değerlendirmesi/2) |
| r03 | mevzuat | Veri sorumlusu ilgili kişinin başvurusunu en geç kaç gün içinde sonuçlandırmalı? | kvkk:13, basvuru-teblig:6 | 1 | 2 | 1 | Başvuru Tebliği m. 6; 6698 s. KVKK m. 13; KVKK Kurulu K. 2024/540 (Kurulun değerlendirmesi/6) |
| r04 | mevzuat | İş sözleşmesine konulan deneme süresi en fazla ne kadar olabilir? | is-kanunu:15 | 1 | 1 | 1 | 4857 s. İş Kanunu m. 15; 4857 s. İş Kanunu m. 53; KVKK Kurulu K. 2024/1361 (veri sorumlusunun savunması/1) |
| r05 | mevzuat | Fazla mesai ücreti normal ücrete göre yüzde kaç zamlı ödenir? | is-kanunu:41, fazla-calisma-yon:4 | 1 | 1 | 1 | 4857 s. İş Kanunu m. 41/2; Fazla Çalışma Yön. m. 4/1; KVKK Kurulu K. 2021/1258 (veri sorumlusunun savunması/1) |
| r06 | mevzuat | Beş yıldan fazla çalışmış bir işçinin yıllık izni kaç gündür? | is-kanunu:53, yillik-izin-yon:9 | 1 | 1 | 1 | Yıllık Ücretli İzin Yön. m. 9; 4857 s. İş Kanunu m. 53; KVKK Kurulu K. 2021/1258 (veri sorumlusunun savunması/1) |
| r07 | mevzuat | Haftalık çalışma süresi en çok kaç saattir? | is-kanunu:63, calisma-sureleri-yon:4 | 1 | 1 | 1 | Çalışma Süreleri Yön. m. 4; 4857 s. İş Kanunu m. 63; KVKK Kurulu K. 2023/86 (Kurulun değerlendirmesi/12) |
| r08 | mevzuat | Kıdem tazminatına hak kazanmak için işyerinde en az ne kadar çalışmak gerekir? | is-kanunu-1475:14 | 1 | 2 | 2 | 4857 s. İş Kanunu m. 112/3; 1475 s. İş Kanunu m. 14/2; KVKK Kurulu K. 2022/797 (Kurulun değerlendirmesi/3) |
| r09 | mevzuat | Saklama ve imha politikası olan şirket periyodik imhayı en geç kaç ayda bir yapmalı? | imha-yon:11 | 1 | 2 | 1 | Silme-İmha Yön. m. 6; Silme-İmha Yön. m. 11; KVKK Kurulu K. 2024/444 (veri sorumlusunun savunması/12) |
| r10 | mevzuat | 2026 yılında net asgari ücret ne kadardır? | kapsam dışı | top1 0.526: 4857 s. İş Kanunu m. 39 | top1 10.467: 4857 s. İş Kanunu m. 39 | top1 0.033: 4857 s. İş Kanunu m. 39 | 4857 s. İş Kanunu m. 39; 4857 s. İş Kanunu geç. m. 3; KVKK Kurulu K. 2026/1183 (karar (hüküm)) |
| k01 | karar | İşveren işyerindeki güvenlik kamerasıyla ses kaydı alabilir mi? | kvkk-karar-2023-2007 | 1 | 1 | 1 | 4857 s. İş Kanunu m. 3/4; 4857 s. İş Kanunu m. 7/9; KVKK Kurulu K. 2023/2007 (şikâyet veya ihlal bildirimi) |
| k02 | karar | Şirket çalışanların kurumsal e-postalarını izleyebilir mi? | kvkk-karar-2023-86 | 1 | 1 | 1 | Yurt Dışı Aktarım Yön. m. 13/1; Yurt Dışı Aktarım Yön. m. 12; KVKK Kurulu K. 2023/86 (veri sorumlusunun savunması/4) |
| k03 | karar | Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyebilir mi? | kvkk-karar-2023-426 | 1 | 1 | 1 | 4857 s. İş Kanunu m. 32/7; 4857 s. İş Kanunu m. 51; KVKK Kurulu K. 2023/426 (Kurulun değerlendirmesi/8) |
| k04 | karar | Spor salonu üyelerden kan grubu bilgisi alabilir mi? | kvkk-karar-2022-1357 | 1 | 1 | 1 | 6698 s. KVKK m. 23; 6698 s. KVKK m. 21/10; KVKK Kurulu K. 2022/1357 (şikâyet veya ihlal bildirimi) |

mevzuat isabet (9 soru): dense 9/9, bm25 9/9, hybrid 9/9
karar isabet (4 soru): dense 4/4, bm25 4/4, hybrid 4/4
