# Değerlendirme — ollama:qwen2.5:7b

Tarih: 2026-11-13 13:40 | commit: c3dac88 | eşik: 0.637 | soru: 56 (50 kapsam içi, 6 kapsam dışı) | hata: 0

Beklenen cevaplar TASLAK (kullanıcı doğrulaması bekliyor). `icerik` anahtar kelime eşleşmesidir; kesin doğruluk için ham cevaplar elle okunmalı.

## Kapsam içi

| Ölçüt | Tümü | Mevzuat | Karar |
|---|---|---|---|
| Beklenen kaynak bağlamda | 45/50 (%90) | 36/41 (%88) | 9/9 (%100) |
| Beklenen kaynağa atıf | 35/50 (%70) | 31/41 (%76) | 4/9 (%44) |
| Cevap içeriği (anahtar) | 35/50 (%70) | 31/41 (%76) | 4/9 (%44) |
| **Doğru (cevap + atıf + içerik)** | 33/50 (%66) | 29/41 (%71) | 4/9 (%44) |
| Yanlış "bilmiyorum" | 12/50 (%24) | 7/41 (%17) | 5/9 (%56) |

Yanlış "bilmiyorum" katmanları: {'arama_esigi': 7, 'llm': 3, 'atif_dogrulama': 2}

## Kapsam dışı

Doğru "bilmiyorum": 6/6 (%100) — katmanlar: {'arama_esigi': 6}

## Diğer

Geçersiz atıf (bağlamda olmayan [n]): 0 | süre medyan 2.86 sn, en uzun 36.4 sn

## Başarısız sorular

| # | Soru | Bağlam | Atıf | İçerik | Not |
|---|---|---|---|---|---|
| e02 | İş güvencesi hükümlerinden yararlanmak için işyerinde en az kaç işçi çalışıyor olmalı? | ✗ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e07 | Bir yılda en fazla kaç saat fazla çalışma yaptırılabilir? | ✓ | ✓ | ✗ | Bir yılda en fazla 267 saatten fazla çalışma yaptırılamaz. [1][2] |
| e13 | Günlük çalışma süresi en fazla kaç saat olabilir? | ✗ | ✗ | ✗ | Günlük çalışma süresi en fazla on beş yaşını tamamlamamış çocuklar için sekiz saat, on beş yaşını tamamlamış o |
| e17 | Eşit davranma ilkesine aykırılık halinde işçi ne kadar tazminat isteyebilir? | ✓ | ✗ | ✗ | bilmiyorum (llm) |
| e21 | İzin kurulu hangi büyüklükteki işyerlerinde kurulur ve kaç kişiden oluşur? | ✓ | ✓ | ✗ | İzin kurulu, işçi sayısı舍不得气喘吁吁地 user  işçi sayısı舍不得气喘吁吁地 深交工会成立的公司中，工会成员可以担任哪些职务？ CEVAP_YOK  CEVAP: Kaynakla |
| e24 | Denkleştirme hangi süre içinde tamamlanmalıdır? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e25 | KVKK'ya göre açık rıza nasıl tanımlanır? | ✗ | ✗ | ✓ | KVKK'ya göre açık rıza, "belirli bir konuya ilişkin, bilgilendirilmeye dayanan ve özgür iradeyle açıklanan rız |
| e27 | Kişisel veriler hangi durumda silinmek, yok edilmek veya anonim hale getirilmek zorundadır? | ✗ | ✗ | ✓ | Kişisel verilerin silinmesi, yok edilmesi veya anonim hale getirilmesi, işlenmesini gerektiren sebeplerin orta |
| e35 | Silme ve yok etme işlemlerine ilişkin kayıtlar en az kaç yıl saklanır? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e37 | Açık rızaya dayanan işlemede aydınlatma ile açık rıza birlikte alınabilir mi? | ✗ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e38 | İşveren, işten çıkardığı çalışanı şirketin sosyal medya hesabından duyurursa Kurul ne karar vermiştir? | ✓ | ✗ | ✗ | bilmiyorum (llm) |
| e39 | İnternet sitesinde reklam çerezlerinin açık rıza alınmadan kullanılması hakkında Kurul hangi yaptırımı uygulamıştır? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e42 | İşyerindeki kameraların konumu hakkında Kurul işverene ne talimat vermiştir? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e43 | Banka çalışanı kendi telefon görüşmesi kayıtlarını isterse, Kurul kararına göre banka bunları nasıl vermelidir? | ✓ | ✗ | ✗ | bilmiyorum (llm) |
| e45 | Doktorun hastanın ameliyat fotoğrafını kendi sosyal medyasında paylaşması üzerine Kurul ilgili kişiyi hangi konuda bilgilendirmiştir? | ✓ | ✗ | ✗ | bilmiyorum (atif_dogrulama) |
| e49 | Ciddi ve yakın tehlike nedeniyle çalışmaktan kaçınan çalışanın o dönemdeki ücreti ne olur? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e50 | Altı aydan fazla işten uzak kalan çalışana tekrar işe başlamadan önce hangi eğitim verilir? | ✓ | ✗ | ✗ | bilmiyorum (atif_dogrulama) |
