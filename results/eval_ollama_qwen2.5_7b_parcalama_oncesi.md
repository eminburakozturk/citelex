# Değerlendirme — ollama:qwen2.5:7b

Tarih: 2026-11-13 13:28 | commit: c3dac88 | eşik: 0.637 | soru: 56 (50 kapsam içi, 6 kapsam dışı) | hata: 0

Beklenen cevaplar TASLAK (kullanıcı doğrulaması bekliyor). `icerik` anahtar kelime eşleşmesidir; kesin doğruluk için ham cevaplar elle okunmalı.

## Kapsam içi

| Ölçüt | Tümü | Mevzuat | Karar |
|---|---|---|---|
| Beklenen kaynak bağlamda | 45/50 (%90) | 36/41 (%88) | 9/9 (%100) |
| Beklenen kaynağa atıf | 36/50 (%72) | 31/41 (%76) | 5/9 (%56) |
| Cevap içeriği (anahtar) | 34/50 (%68) | 30/41 (%73) | 4/9 (%44) |
| **Doğru (cevap + atıf + içerik)** | 32/50 (%64) | 28/41 (%68) | 4/9 (%44) |
| Yanlış "bilmiyorum" | 10/50 (%20) | 6/41 (%15) | 4/9 (%44) |

Yanlış "bilmiyorum" katmanları: {'arama_esigi': 7, 'llm': 3}

## Kapsam dışı

Doğru "bilmiyorum": 6/6 (%100) — katmanlar: {'arama_esigi': 6}

## Diğer

Geçersiz atıf (bağlamda olmayan [n]): 0 | süre medyan 2.62 sn, en uzun 40.34 sn

## Başarısız sorular

| # | Soru | Bağlam | Atıf | İçerik | Not |
|---|---|---|---|---|---|
| e02 | İş güvencesi hükümlerinden yararlanmak için işyerinde en az kaç işçi çalışıyor olmalı? | ✗ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e07 | Bir yılda en fazla kaç saat fazla çalışma yaptırılabilir? | ✓ | ✓ | ✗ | Bir yılda en fazla 267 saatten fazla çalışma yaptırılamaz. [1][2] |
| e13 | Günlük çalışma süresi en fazla kaç saat olabilir? | ✗ | ✗ | ✗ | Günlük çalışma süresi en fazla on beş yaşını tamamlamamış çocuklar için sekiz saat, on beş yaşını tamamlamış o |
| e16 | Özel sektör işyerinde kaç işçiden itibaren ve yüzde kaç oranında engelli çalıştırmak zorunludur? | ✓ | ✓ | ✗ | Özel sektör işyerlerinde 50 veya daha fazla işçi çalıştırdıkları işyerlerinde, işçisi 3% oranında engelli çalı |
| e17 | Eşit davranma ilkesine aykırılık halinde işçi ne kadar tazminat isteyebilir? | ✓ | ✗ | ✗ | bilmiyorum (llm) |
| e21 | İzin kurulu hangi büyüklükteki işyerlerinde kurulur ve kaç kişiden oluşur? | ✓ | ✓ | ✗ | İzin kurulu, işçi sayısı舍不得气喘吁吁地 user  işçi sayısı舍不得气喘吁吁地 深交工会成立的公司中，工会成员可以担任哪些职务？ CEVAP_YOK  CEVAP: Kaynakla |
| e24 | Denkleştirme hangi süre içinde tamamlanmalıdır? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e25 | KVKK'ya göre açık rıza nasıl tanımlanır? | ✗ | ✗ | ✓ | KVKK'ya göre açık rıza, "belirli bir konuya ilişkin, bilgilendirilmeye dayanan ve özgür iradeyle açıklanan rız |
| e27 | Kişisel veriler hangi durumda silinmek, yok edilmek veya anonim hale getirilmek zorundadır? | ✗ | ✗ | ✓ | Kişisel verilerin silinmesi, yok edilmesi veya anonim hale getirilmesi, işlenmesini gerektiren sebeplerin orta |
| e30 | Kurul şikâyete süresinde cevap vermezse ne olur? | ✓ | ✗ | ✗ | Kurul, şikâyete verilen cevap süresini aşarsa, şikayetçi otuz ve her hâlde şikayet tarihinden itibaren altmış  |
| e35 | Silme ve yok etme işlemlerine ilişkin kayıtlar en az kaç yıl saklanır? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e37 | Açık rızaya dayanan işlemede aydınlatma ile açık rıza birlikte alınabilir mi? | ✗ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e38 | İşveren, işten çıkardığı çalışanı şirketin sosyal medya hesabından duyurursa Kurul ne karar vermiştir? | ✓ | ✗ | ✗ | bilmiyorum (llm) |
| e39 | İnternet sitesinde reklam çerezlerinin açık rıza alınmadan kullanılması hakkında Kurul hangi yaptırımı uygulamıştır? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e42 | İşyerindeki kameraların konumu hakkında Kurul işverene ne talimat vermiştir? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e43 | Banka çalışanı kendi telefon görüşmesi kayıtlarını isterse, Kurul kararına göre banka bunları nasıl vermelidir? | ✓ | ✗ | ✗ | bilmiyorum (llm) |
| e45 | Doktorun hastanın ameliyat fotoğrafını kendi sosyal medyasında paylaşması üzerine Kurul ilgili kişiyi hangi konuda bilgilendirmiştir? | ✓ | ✓ | ✗ | Kurul, ilgili hastanın ameliyat fotoğrafının kendi sosyal medyasında paylaşan doktora idari para cezası uygula |
| e49 | Ciddi ve yakın tehlike nedeniyle çalışmaktan kaçınan çalışanın o dönemdeki ücreti ne olur? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
