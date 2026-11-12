# "Bilmiyorum" eşiği kalibrasyonu

Sinyal: dense top-1 benzerliği. Eşik = kapsam içi en düşük skor (0.594) - 0.02 = **0.574**.

| # | Kapsam | Soru | dense top-1 | En yakın kaynak | Eşik sonucu |
|---|---|---|---|---|---|
| c03 | ic | Kişisel veriler hangi durumlarda yurt dışına aktarılabilir? | 0.816 | Yurt Dışı Aktarım Yön. m. 6 | geçer |
| c23 | ic | Uçakta internet kullanmak için açık rıza istenmesi doğru mu? | 0.764 | KVKK Kurulu K. 2024/1393 (şikâyet veya ihlal bildirimi) | geçer |
| c04 | ic | Veri sorumlusu aydınlatma yaparken hangi bilgileri vermek zorunda? | 0.751 | Aydınlatma Tebliği m. 5 | geçer |
| c17 | ic | On sekiz yaşından küçük işçiler gece çalıştırılabilir mi? | 0.749 | 4857 s. İş Kanunu m. 73 | geçer |
| c02 | ic | Gece çalışması en fazla kaç saat sürebilir? | 0.744 | 4857 s. İş Kanunu m. 69/1 | geçer |
| c13 | ic | İşveren çalışma koşullarımı tek taraflı değiştirebilir mi? | 0.729 | 4857 s. İş Kanunu m. 22 | geçer |
| c01 | ic | İşçi iş sözleşmesini feshederken ne kadar önceden haber vermeli? | 0.720 | 4857 s. İş Kanunu m. 25/1 | geçer |
| c18 | ic | Kişisel veriler başka bir şirkete hangi şartla aktarılabilir? | 0.712 | Yurt Dışı Aktarım Yön. m. 10 | geçer |
| c16 | ic | İşten ayrılırken kullanmadığım yıllık izinler ne olur? | 0.703 | 4857 s. İş Kanunu m. 54 | geçer |
| c21 | ic | Banka mobil uygulamada yüz tanımayla şifre belirletebilir mi? | 0.701 | KVKK Kurulu K. 2023/1310 (Kurulun değerlendirmesi/4) | geçer |
| c14 | ic | Belirli süreli iş sözleşmesi üst üste yenilenebilir mi? | 0.696 | 4857 s. İş Kanunu m. 11 | geçer |
| c22 | ic | Borcumu kapattım, kredi kayıt bürosundaki kaydımın silinmesini isteyebilir miyim? | 0.690 | KVKK Kurulu K. 2024/444 (şikâyet veya ihlal bildirimi) | geçer |
| c15 | ic | Bayramda çalışan işçiye ne kadar ücret ödenir? | 0.688 | 4857 s. İş Kanunu m. 47 | geçer |
| c12 | ic | İşveren hangi davranışlar yüzünden işçiyi bildirimsiz işten çıkarabilir? | 0.677 | 4857 s. İş Kanunu m. 25/1 | geçer |
| c24 | dis_yakin | Yıllık izin ücretinden gelir vergisi kesilir mi? | 0.664 | 4857 s. İş Kanunu m. 57 | geçer |
| c20 | ic | Kripto borsası üyelik seviyemi yükseltmek için fazladan belge isteyebilir mi? | 0.663 | KVKK Kurulu K. 2023/570 (şikâyet veya ihlal bildirimi) | geçer |
| c05 | ic | Hastane reklamlarında hasta fotoğrafı kullanılabilir mi? | 0.657 | KVKK Kurulu K. 2023/787 (şikâyet veya ihlal bildirimi/1) | geçer |
| c26 | dis_yakin | İşyeri hekimi bulundurma zorunluluğu kaç işçiden itibaren başlar? | 0.633 | 4857 s. İş Kanunu m. 30/1 | geçer |
| c11 | ic | Maaşım ödenmiyor, hemen istifa edebilir miyim? | 0.629 | 4857 s. İş Kanunu m. 25/1 | geçer |
| c27 | dis_yakin | Avrupa Birliği'nde kişisel verilerin korunması hangi tüzükle düzenlenir? | 0.626 | KVKK Kurulu K. 2022/31 (Kurulun değerlendirmesi/1) | geçer |
| c25 | dis_yakin | Toplu iş sözleşmesi en fazla kaç yıl için yapılabilir? | 0.621 | 4857 s. İş Kanunu m. 7/3 | geçer |
| c08 | dis_yakin | İşsizlik maaşı kaç ay boyunca ödenir? | 0.610 | 4857 s. İş Kanunu m. 21/3 | geçer |
| c19 | ic | KVKK hangi durumlarda uygulanmaz? | 0.594 | KVKK Kurulu K. 2021/1051 (Kurulun değerlendirmesi/2) | geçer |
| c07 | dis_yakin | Emekli olmak için kaç gün prim ödemek gerekir? | 0.574 | 4857 s. İş Kanunu m. 61 | KESİLİR |
| c09 | dis_uzak | Boşanma davasında nafaka nasıl belirlenir? | 0.539 | 4857 s. İş Kanunu m. 21/4 | KESİLİR |
| c30 | dis_uzak | Yıllık gelir vergisi beyannamesi hangi ayda verilir? | 0.519 | Yıllık Ücretli İzin Yön. m. 10 | KESİLİR |
| c28 | dis_uzak | Apartman aidatını ödemeyen kat malikine hangi gecikme faizi uygulanır? | 0.519 | 1475 s. İş Kanunu m. 14/11 | KESİLİR |
| c29 | dis_uzak | Pasaport harcı ne kadardır? | 0.500 | Başvuru Tebliği m. 7 | KESİLİR |
| c06 | dis_yakin | Ev sahibi kirayı yılda en fazla yüzde kaç artırabilir? | 0.473 | 4857 s. İş Kanunu m. 57 | KESİLİR |
| c10 | dis_uzak | Ehliyet sınavında kaç soru sorulur? | 0.450 | 6698 s. KVKK geç. m. 2 | KESİLİR |

dis_yakin: 2/7 soru eşikte kesiliyor (skor aralığı 0.473–0.664)

dis_uzak: 5/5 soru eşikte kesiliyor (skor aralığı 0.450–0.539)

Not: 30 soru; eşik kaba bir ilk filtredir. Eşiği geçen kapsam dışı sorular LLM katmanına (CEVAP_YOK) kalır.
