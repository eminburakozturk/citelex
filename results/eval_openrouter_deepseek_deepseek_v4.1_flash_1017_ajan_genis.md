# Değerlendirme — openrouter:deepseek/deepseek-v4.1-flash-1017

Tarih: 2026-11-14 22:55 | commit: 001896b | eşik: 0.637 | reranker: kapalı | soru: 56 (50 kapsam içi, 6 kapsam dışı) | hata: 0

Beklenen cevaplar TASLAK (kullanıcı doğrulaması bekliyor). `icerik` anahtar kelime eşleşmesidir; kesin doğruluk için ham cevaplar elle okunmalı.

## Kapsam içi

| Ölçüt | Tümü | Mevzuat | Karar |
|---|---|---|---|
| Beklenen kaynak bağlamda | 45/50 (%90) | 36/41 (%88) | 9/9 (%100) |
| Beklenen kaynağa atıf | 45/50 (%90) | 36/41 (%88) | 9/9 (%100) |
| Cevap içeriği (anahtar) | 47/50 (%94) | 39/41 (%95) | 8/9 (%89) |
| **Doğru (cevap + atıf + içerik)** | 44/50 (%88) | 36/41 (%88) | 8/9 (%89) |
| Yanlış "bilmiyorum" | 0/50 (%0) | 0/41 (%0) | 0/9 (%0) |

Yanlış "bilmiyorum" katmanları: —

## Kapsam dışı

Doğru "bilmiyorum": 5/6 (%83) — katmanlar: {'llm': 4, 'arama_esigi': 1}

## Diğer

Geçersiz atıf (bağlamda olmayan [n]): 0 | süre medyan 2.23 sn, en uzun 17.56 sn

## Başarısız sorular

| # | Soru | Bağlam | Atıf | İçerik | Not |
|---|---|---|---|---|---|
| e13 | Günlük çalışma süresi en fazla kaç saat olabilir? | ✗ | ✗ | ✓ | Günlük çalışma süresi her ne şekilde olursa olsun 11 saati aşamaz [5]. Genel bakımdan çalışma süresi ise hafta |
| e24 | Denkleştirme hangi süre içinde tamamlanmalıdır? | ✗ | ✗ | ✗ | 4857 sayılı İş Kanunu'na göre, nitelikleri gereği günlük ve haftalık çalışma sürelerinin olağan şekilde uygula |
| e25 | KVKK'ya göre açık rıza nasıl tanımlanır? | ✗ | ✗ | ✓ | KVKK'ya göre açık rıza, "belirli bir konuya ilişkin, bilgilendirilmeye dayanan ve özgür iradeyle açıklanan rız |
| e27 | Kişisel veriler hangi durumda silinmek, yok edilmek veya anonim hale getirilmek zorundadır? | ✗ | ✗ | ✗ | Kanunun 5 inci ve 6 ncı maddelerinde yer alan kişisel verilerin işlenme şartlarının tamamının ortadan kalkması |
| e37 | Açık rızaya dayanan işlemede aydınlatma ile açık rıza birlikte alınabilir mi? | ✗ | ✗ | ✓ | Hayır, aydınlatma yükümlülüğü ile açık rıza alınması işlemlerinin ayrı ayrı yerine getirilmesi gerekir [1][2]. |
| e38 | İşveren, işten çıkardığı çalışanı şirketin sosyal medya hesabından duyurursa Kurul ne karar vermiştir? | ✓ | ✓ | ✗ | Kurul, 2022/386 sayılı kararında, iş akdi sonlandırılan ilgili kişinin açık ad-soyadı ve hakkındaki ithamları  |
| d03 | İş mahkemesinde dava açmadan önce arabuluculuk görüşmeleri en fazla kaç hafta sürer? | — | — | — | CEVAP VERDİ: İş mahkemesinde dava şartı olarak arabuluculuğa başvurulduğunda, arabulucu yapılan başvuruyu görevlendirildiği |
