# Değerlendirme — openrouter:deepseek/deepseek-v4.1-flash-1017

Tarih: 2026-11-13 20:39 | commit: a6958d2 | eşik: 0.637 | reranker: kapalı | soru: 56 (50 kapsam içi, 6 kapsam dışı) | hata: 0

Beklenen cevaplar TASLAK (kullanıcı doğrulaması bekliyor). `icerik` anahtar kelime eşleşmesidir; kesin doğruluk için ham cevaplar elle okunmalı.

## Kapsam içi

| Ölçüt | Tümü | Mevzuat | Karar |
|---|---|---|---|
| Beklenen kaynak bağlamda | 45/50 (%90) | 36/41 (%88) | 9/9 (%100) |
| Beklenen kaynağa atıf | 45/50 (%90) | 36/41 (%88) | 9/9 (%100) |
| Cevap içeriği (anahtar) | 47/50 (%94) | 39/41 (%95) | 8/9 (%89) |
| **Doğru (cevap + atıf + içerik)** | 44/50 (%88) | 36/41 (%88) | 8/9 (%89) |
| Yanlış "bilmiyorum" | 1/50 (%2) | 1/41 (%2) | 0/9 (%0) |

Yanlış "bilmiyorum" katmanları: {'arama_esigi': 1}

## Kapsam dışı

Doğru "bilmiyorum": 6/6 (%100) — katmanlar: {'llm': 1, 'arama_esigi': 5}

## Diğer

Geçersiz atıf (bağlamda olmayan [n]): 0 | süre medyan 2.42 sn, en uzun 118.65 sn

## Başarısız sorular

| # | Soru | Bağlam | Atıf | İçerik | Not |
|---|---|---|---|---|---|
| e13 | Günlük çalışma süresi en fazla kaç saat olabilir? | ✗ | ✗ | ✓ | Günlük çalışma süresi her ne şekilde olursa olsun 11 saati aşamaz [5]. Genel bakımdan çalışma süresi ise hafta |
| e24 | Denkleştirme hangi süre içinde tamamlanmalıdır? | ✗ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e25 | KVKK'ya göre açık rıza nasıl tanımlanır? | ✗ | ✗ | ✓ | Açık rıza, KVKK kapsamında "belirli bir konuya ilişkin, bilgilendirilmeye dayanan ve özgür iradeyle açıklanan  |
| e27 | Kişisel veriler hangi durumda silinmek, yok edilmek veya anonim hale getirilmek zorundadır? | ✗ | ✗ | ✗ | Kanunun 5. ve 6. maddelerinde yer alan kişisel verilerin işlenme şartlarının tamamının ortadan kalkması halind |
| e37 | Açık rızaya dayanan işlemede aydınlatma ile açık rıza birlikte alınabilir mi? | ✗ | ✗ | ✓ | Aydınlatma yükümlülüğü ile açık rızanın ayrı ayrı yerine getirilmesi gerekir; Kurul, iş sözleşmesine eklenen v |
| e38 | İşveren, işten çıkardığı çalışanı şirketin sosyal medya hesabından duyurursa Kurul ne karar vermiştir? | ✓ | ✓ | ✗ | Kurul, 2022/386 sayılı kararında, iş akdi sonlandırılan ilgili kişinin açık ad-soyadı ve hakkındaki ithamları  |
