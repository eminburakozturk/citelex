# Değerlendirme — ollama:qwen2.5:7b

Tarih: 2026-11-12 17:48 | commit: 9076480 | eşik: 0.637 | soru: 52 (46 kapsam içi, 6 kapsam dışı) | hata: 0

Beklenen cevaplar TASLAK (kullanıcı doğrulaması bekliyor). `icerik` anahtar kelime eşleşmesidir; kesin doğruluk için ham cevaplar elle okunmalı.

## Kapsam içi

| Ölçüt | Tümü | Mevzuat | Karar |
|---|---|---|---|
| Beklenen kaynak bağlamda | 41/46 (%89) | 32/37 (%86) | 9/9 (%100) |
| Beklenen kaynağa atıf | 33/46 (%72) | 28/37 (%76) | 5/9 (%56) |
| Cevap içeriği (anahtar) | 34/46 (%74) | 29/37 (%78) | 5/9 (%56) |
| **Doğru (cevap + atıf + içerik)** | 31/46 (%67) | 26/37 (%70) | 5/9 (%56) |
| Yanlış "bilmiyorum" | 9/46 (%20) | 5/37 (%14) | 4/9 (%44) |

Yanlış "bilmiyorum" katmanları: {'arama_esigi': 6, 'llm': 3}

## Kapsam dışı

Doğru "bilmiyorum": 6/6 (%100) — katmanlar: {'arama_esigi': 6}

## Diğer

Geçersiz atıf (bağlamda olmayan [n]): 0 | süre medyan 4.78 sn, en uzun 25.95 sn

## Başarısız sorular

| # | Soru | Bağlam | Atıf | İçerik | Not |
|---|---|---|---|---|---|
| e02 | İş güvencesi hükümlerinden yararlanmak için işyerinde en az kaç işçi çalışıyor olmalı? | ✗ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e07 | Bir yılda en fazla kaç saat fazla çalışma yaptırılabilir? | ✓ | ✓ | ✗ | Bir yılda en fazla 267 saatten fazla çalışma yaptırılamaz. [1][2] |
| e13 | Günlük çalışma süresi en fazla kaç saat olabilir? | ✗ | ✗ | ✓ | Günlük çalışma süresi en fazla on beş yaşını tamamlamamış çocukların hafif işlerde çalıştırıldığı sanat, kültü |
| e17 | Eşit davranma ilkesine aykırılık halinde işçi ne kadar tazminat isteyebilir? | ✓ | ✗ | ✗ | bilmiyorum (llm) |
| e21 | İzin kurulu hangi büyüklükteki işyerlerinde kurulur ve kaç kişiden oluşur? | ✓ | ✓ | ✗ | İzin kurulu işçi sayısı舍不得流汗不流泪 user İzin kurulu işçi sayısı daha fazla olan işyerlerinde kurulur ve toplam üç |
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
