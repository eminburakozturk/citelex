# Değerlendirme — openrouter:deepseek/deepseek-v4.1-flash-1017

Tarih: 2026-11-14 20:51 | commit: 453b9e0 | eşik: 0.637 | reranker: kapalı | soru: 56 (50 kapsam içi, 6 kapsam dışı) | hata: 0

Beklenen cevaplar TASLAK (kullanıcı doğrulaması bekliyor). `icerik` anahtar kelime eşleşmesidir; kesin doğruluk için ham cevaplar elle okunmalı.

## Kapsam içi

| Ölçüt | Tümü | Mevzuat | Karar |
|---|---|---|---|
| Beklenen kaynak bağlamda | 46/50 (%92) | 37/41 (%90) | 9/9 (%100) |
| Beklenen kaynağa atıf | 45/50 (%90) | 37/41 (%90) | 8/9 (%89) |
| Cevap içeriği (anahtar) | 47/50 (%94) | 40/41 (%98) | 7/9 (%78) |
| **Doğru (cevap + atıf + içerik)** | 44/50 (%88) | 37/41 (%90) | 7/9 (%78) |
| Yanlış "bilmiyorum" | 0/50 (%0) | 0/41 (%0) | 0/9 (%0) |

Yanlış "bilmiyorum" katmanları: —

## Kapsam dışı

Doğru "bilmiyorum": 4/6 (%67) — katmanlar: {'llm': 3, 'arama_esigi': 1}

## Diğer

Geçersiz atıf (bağlamda olmayan [n]): 0 | süre medyan 2.23 sn, en uzun 28.15 sn

## Başarısız sorular

| # | Soru | Bağlam | Atıf | İçerik | Not |
|---|---|---|---|---|---|
| e13 | Günlük çalışma süresi en fazla kaç saat olabilir? | ✗ | ✗ | ✓ | Günlük çalışma süresi her ne şekilde olursa olsun 11 saati aşamaz [5]. Genel bakımdan çalışma süresi ise hafta |
| e25 | KVKK'ya göre açık rıza nasıl tanımlanır? | ✗ | ✗ | ✓ | Açık rıza, Kanun'un "Tanımlar" başlıklı maddesinde "belirli bir konuya ilişkin, bilgilendirilmeye dayanan ve ö |
| e27 | Kişisel veriler hangi durumda silinmek, yok edilmek veya anonim hale getirilmek zorundadır? | ✗ | ✗ | ✗ | Kanunun 5. ve 6. maddelerinde yer alan kişisel verilerin işlenme şartlarının tamamının ortadan kalkması halind |
| e37 | Açık rızaya dayanan işlemede aydınlatma ile açık rıza birlikte alınabilir mi? | ✗ | ✗ | ✓ | Aydınlatma ile açık rızanın ayrı ayrı yerine getirilmesi gerekir; Kurul, iş sözleşmesine eklenen ve hem aydınl |
| e38 | İşveren, işten çıkardığı çalışanı şirketin sosyal medya hesabından duyurursa Kurul ne karar vermiştir? | ✓ | ✓ | ✗ | İş akdinin sonlandırılmasının şirketin sosyal medya hesabından duyurulmasına ilişkin somut olayda Kurul, ilgil |
| e39 | İnternet sitesinde reklam çerezlerinin açık rıza alınmadan kullanılması hakkında Kurul hangi yaptırımı uygulamıştır? | ✓ | ✗ | ✗ | Kurul, bir kararında internet sitesinde kesinlikle gerekli olmayan analitik çerezlerin açık rıza alınmaksızın  |
| d03 | İş mahkemesinde dava açmadan önce arabuluculuk görüşmeleri en fazla kaç hafta sürer? | — | — | — | CEVAP VERDİ: İş mahkemesinde dava açılmadan önce yapılan arabuluculukta arabulucu, başvuruyu görevlendirildiği tarihten iti |
| d05 | Anonim şirket en az kaç ortakla kurulabilir? | — | — | — | CEVAP VERDİ: Anonim şirketin kurulabilmesi için pay sahibi olan bir veya daha fazla kurucunun varlığı şarttır [6]. |
