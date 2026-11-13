# Değerlendirme — openrouter:deepseek/deepseek-v4.1-flash-1017

Tarih: 2026-11-13 20:59 | commit: 9f2760d | eşik: 0.637 | reranker: açık | soru: 56 (50 kapsam içi, 6 kapsam dışı) | hata: 0

Beklenen cevaplar TASLAK (kullanıcı doğrulaması bekliyor). `icerik` anahtar kelime eşleşmesidir; kesin doğruluk için ham cevaplar elle okunmalı.

## Kapsam içi

| Ölçüt | Tümü | Mevzuat | Karar |
|---|---|---|---|
| Beklenen kaynak bağlamda | 46/50 (%92) | 37/41 (%90) | 9/9 (%100) |
| Beklenen kaynağa atıf | 46/50 (%92) | 37/41 (%90) | 9/9 (%100) |
| Cevap içeriği (anahtar) | 48/50 (%96) | 40/41 (%98) | 8/9 (%89) |
| **Doğru (cevap + atıf + içerik)** | 45/50 (%90) | 37/41 (%90) | 8/9 (%89) |
| Yanlış "bilmiyorum" | 0/50 (%0) | 0/41 (%0) | 0/9 (%0) |

Yanlış "bilmiyorum" katmanları: —

## Kapsam dışı

Doğru "bilmiyorum": 6/6 (%100) — katmanlar: {'llm': 2, 'arama_esigi': 4}

## Diğer

Geçersiz atıf (bağlamda olmayan [n]): 0 | süre medyan 3.98 sn, en uzun 34.33 sn

## Başarısız sorular

| # | Soru | Bağlam | Atıf | İçerik | Not |
|---|---|---|---|---|---|
| e13 | Günlük çalışma süresi en fazla kaç saat olabilir? | ✗ | ✗ | ✓ | Günlük çalışma süresi her ne şekilde olursa olsun 11 saati aşamaz [1]. Telafi çalışmaları da günlük en çok çal |
| e24 | Denkleştirme hangi süre içinde tamamlanmalıdır? | ✗ | ✗ | ✗ | Denkleştirme esasının uygulandığı hallerde, işçinin haftalık ortalama çalışma süresinin normal haftalık iş sür |
| e25 | KVKK'ya göre açık rıza nasıl tanımlanır? | ✗ | ✗ | ✓ | Açık rıza, Kanun'un tanımlar maddesinde "belirli bir konuya ilişkin, bilgilendirilmeye dayanan ve özgür iradey |
| e37 | Açık rızaya dayanan işlemede aydınlatma ile açık rıza birlikte alınabilir mi? | ✗ | ✗ | ✓ | Hayır, birlikte alınamaz; aydınlatma yükümlülüğü ile açık rıza alınması işlemlerinin ayrı ayrı yerine getirilm |
| e38 | İşveren, işten çıkardığı çalışanı şirketin sosyal medya hesabından duyurursa Kurul ne karar vermiştir? | ✓ | ✓ | ✗ | İş akdi sonlandırılan çalışanın açık ad-soyadı ve hakkındaki ithamları içeren duyurunun şirketin herkese açık  |
