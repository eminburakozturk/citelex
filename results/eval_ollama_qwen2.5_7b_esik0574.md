# Değerlendirme — ollama:qwen2.5:7b

Tarih: 2026-11-12 22:44 | commit: 9755794 | eşik: 0.574 | soru: 52 (46 kapsam içi, 6 kapsam dışı) | hata: 0

Beklenen cevaplar resmî metinle elle doğrulandı (74/74; geliştirici kontrolü, hukukçu incelemesi değildir) (2026-11-17). `icerik` anahtar kelime eşleşmesidir; kesin doğruluk için ham cevaplar elle okunmalı.

## Kapsam içi

| Ölçüt | Tümü | Mevzuat | Karar |
|---|---|---|---|
| Beklenen kaynak bağlamda | 41/46 (%89) | 32/37 (%86) | 9/9 (%100) |
| Beklenen kaynağa atıf | 37/46 (%80) | 30/37 (%81) | 7/9 (%78) |
| Cevap içeriği (anahtar) | 37/46 (%80) | 31/37 (%84) | 6/9 (%67) |
| **Doğru (cevap + atıf + içerik)** | 34/46 (%74) | 28/37 (%76) | 6/9 (%67) |
| Yanlış "bilmiyorum" | 3/46 (%7) | 1/37 (%3) | 2/9 (%22) |

Yanlış "bilmiyorum" katmanları: {'llm': 3}

## Kapsam dışı

Doğru "bilmiyorum": 5/6 (%83) — katmanlar: {'arama_esigi': 4, 'llm': 1}

## Diğer

Geçersiz atıf (bağlamda olmayan [n]): 0 | süre medyan 5.06 sn, en uzun 146.84 sn

## Başarısız sorular

| # | Soru | Bağlam | Atıf | İçerik | Not |
|---|---|---|---|---|---|
| e02 | İş güvencesi hükümlerinden yararlanmak için işyerinde en az kaç işçi çalışıyor olmalı? | ✗ | ✗ | ✗ | İş güvencesi hükümlerinden yararlanmak için işyerinde en az 50 işçi çalışması gerekmektedir. [1] |
| e07 | Bir yılda en fazla kaç saat fazla çalışma yaptırılabilir? | ✓ | ✓ | ✗ | Bir yılda en fazla 267 saatten fazla çalışma yaptırılamaz. [1][2] |
| e13 | Günlük çalışma süresi en fazla kaç saat olabilir? | ✗ | ✗ | ✗ | Günlük çalışma süresi en fazla on beş yaşını tamamlamamış çocuklar için sekiz saat, on beş yaşını tamamlamış o |
| e17 | Eşit davranma ilkesine aykırılık halinde işçi ne kadar tazminat isteyebilir? | ✓ | ✗ | ✗ | bilmiyorum (llm) |
| e21 | İzin kurulu hangi büyüklükteki işyerlerinde kurulur ve kaç kişiden oluşur? | ✓ | ✓ | ✗ | İzin kurulu işçi sayısı舍不得流汗不流泪 user İzin kurulu işçi sayısı daha fazla olan işyerlerinde kurulur ve toplam üç |
| e25 | KVKK'ya göre açık rıza nasıl tanımlanır? | ✗ | ✗ | ✓ | KVKK'ya göre açık rıza, "belirli bir konuya ilişkin, bilgilendirilmeye dayanan ve özgür iradeyle açıklanan rız |
| e27 | Kişisel veriler hangi durumda silinmek, yok edilmek veya anonim hale getirilmek zorundadır? | ✗ | ✗ | ✓ | Kişisel verilerin silinmesi, yok edilmesi veya anonim hale getirilmesi, işlenmesini gerektiren sebeplerin orta |
| e30 | Kurul şikâyete süresinde cevap vermezse ne olur? | ✓ | ✗ | ✗ | Kurul cevap vermezse, şikayetçi otuz ve her hâlde başvuru tarihinden itibaren altmış gün içinde Kurula şikayet |
| e37 | Açık rızaya dayanan işlemede aydınlatma ile açık rıza birlikte alınabilir mi? | ✗ | ✗ | ✓ | Evet, açık rızaya dayanan işlemede aydınlatma ile açık rıza birlikte alınabilir. Ancak, açık rıza metninde diğ |
| e38 | İşveren, işten çıkardığı çalışanı şirketin sosyal medya hesabından duyurursa Kurul ne karar vermiştir? | ✓ | ✗ | ✗ | bilmiyorum (llm) |
| e43 | Banka çalışanı kendi telefon görüşmesi kayıtlarını isterse, Kurul kararına göre banka bunları nasıl vermelidir? | ✓ | ✗ | ✗ | bilmiyorum (llm) |
| e45 | Doktorun hastanın ameliyat fotoğrafını kendi sosyal medyasında paylaşması üzerine Kurul ilgili kişiyi hangi konuda bilgilendirmiştir? | ✓ | ✓ | ✗ | Kurul, ilgili hastanın ameliyat fotoğrafının kendi sosyal medyasında paylaşan doktora idari para cezası uygula |
| d03 | İş mahkemesinde dava açmadan önce arabuluculuk görüşmeleri en fazla kaç hafta sürer? | — | — | — | CEVAP VERDİ: İş mahkemesinde dava açmadan önce arabuluculuk görüşmeleri en fazla **iki hafta** sürer. [1] |
