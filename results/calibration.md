# "Bilmiyorum" eşiği kalibrasyonu

Sinyal: dense top-1 benzerliği. Eşik = kapsam içi en düşük skor (0.657) - 0.02 = **0.637**.

| # | Kapsam | Soru | dense top-1 | En yakın kaynak | Eşik sonucu |
|---|---|---|---|---|---|
| c03 | ic | Kişisel veriler hangi durumlarda yurt dışına aktarılabilir? | 0.816 | Yurt Dışı Aktarım Yön. m. 6 | geçer |
| c04 | ic | Veri sorumlusu aydınlatma yaparken hangi bilgileri vermek zorunda? | 0.751 | Aydınlatma Tebliği m. 5 | geçer |
| c02 | ic | Gece çalışması en fazla kaç saat sürebilir? | 0.744 | 4857 s. İş Kanunu m. 69/1 | geçer |
| c01 | ic | İşçi iş sözleşmesini feshederken ne kadar önceden haber vermeli? | 0.720 | 4857 s. İş Kanunu m. 25/1 | geçer |
| c05 | ic | Hastane reklamlarında hasta fotoğrafı kullanılabilir mi? | 0.657 | KVKK Kurulu K. 2023/787 (şikâyet veya ihlal bildirimi/1) | geçer |
| c08 | dis_yakin | İşsizlik maaşı kaç ay boyunca ödenir? | 0.610 | 4857 s. İş Kanunu m. 21/3 | KESİLİR |
| c07 | dis_yakin | Emekli olmak için kaç gün prim ödemek gerekir? | 0.574 | 4857 s. İş Kanunu m. 61 | KESİLİR |
| c09 | dis_uzak | Boşanma davasında nafaka nasıl belirlenir? | 0.539 | 4857 s. İş Kanunu m. 21/4 | KESİLİR |
| c06 | dis_yakin | Ev sahibi kirayı yılda en fazla yüzde kaç artırabilir? | 0.473 | 4857 s. İş Kanunu m. 57 | KESİLİR |
| c10 | dis_uzak | Ehliyet sınavında kaç soru sorulur? | 0.450 | 6698 s. KVKK geç. m. 2 | KESİLİR |

dis_yakin: 3/3 soru eşikte kesiliyor (skor aralığı 0.473–0.610)

dis_uzak: 2/2 soru eşikte kesiliyor (skor aralığı 0.450–0.539)

Not: 10 soru; eşik kaba bir ilk filtredir. Eşiği geçen kapsam dışı sorular LLM katmanına (CEVAP_YOK) kalır.
