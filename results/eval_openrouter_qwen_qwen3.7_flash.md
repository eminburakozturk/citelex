# Değerlendirme — openrouter:qwen/qwen3.7-flash

Tarih: 2026-11-13 14:41 | commit: 8e4d3f2 | eşik: 0.637 | soru: 56 (50 kapsam içi, 6 kapsam dışı) | hata: 0

Beklenen cevaplar TASLAK (kullanıcı doğrulaması bekliyor). `icerik` anahtar kelime eşleşmesidir; kesin doğruluk için ham cevaplar elle okunmalı.

## Kapsam içi

| Ölçüt | Tümü | Mevzuat | Karar |
|---|---|---|---|
| Beklenen kaynak bağlamda | 45/50 (%90) | 36/41 (%88) | 9/9 (%100) |
| Beklenen kaynağa atıf | 39/50 (%78) | 32/41 (%78) | 7/9 (%78) |
| Cevap içeriği (anahtar) | 41/50 (%82) | 34/41 (%83) | 7/9 (%78) |
| **Doğru (cevap + atıf + içerik)** | 39/50 (%78) | 32/41 (%78) | 7/9 (%78) |
| Yanlış "bilmiyorum" | 8/50 (%16) | 6/41 (%15) | 2/9 (%22) |

Yanlış "bilmiyorum" katmanları: {'arama_esigi': 7, 'llm': 1}

## Kapsam dışı

Doğru "bilmiyorum": 6/6 (%100) — katmanlar: {'arama_esigi': 6}

## Diğer

Geçersiz atıf (bağlamda olmayan [n]): 0 | süre medyan 2.39 sn, en uzun 39.85 sn

## Başarısız sorular

| # | Soru | Bağlam | Atıf | İçerik | Not |
|---|---|---|---|---|---|
| e02 | İş güvencesi hükümlerinden yararlanmak için işyerinde en az kaç işçi çalışıyor olmalı? | ✗ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e05 | Ücreti kaç gün ödenmeyen işçi çalışmaktan kaçınabilir? | ✓ | ✗ | ✗ | bilmiyorum (llm) |
| e13 | Günlük çalışma süresi en fazla kaç saat olabilir? | ✗ | ✗ | ✓ | Günlük çalışma süresi her ne şekilde olursa olsun 11 saati aşamaz [5]. Ancak, çocuk ve genç işçiler ile ilgili |
| e24 | Denkleştirme hangi süre içinde tamamlanmalıdır? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e25 | KVKK'ya göre açık rıza nasıl tanımlanır? | ✗ | ✗ | ✓ | KVKK’nın 3’üncü maddesinin (1) numaralı fıkrasının (a) bendinde açık rıza; “belirli bir konuya ilişkin, bilgil |
| e27 | Kişisel veriler hangi durumda silinmek, yok edilmek veya anonim hale getirilmek zorundadır? | ✗ | ✗ | ✗ | Kişisel verilerin silinmesi, yok edilmesi veya anonim hale getirilmesi zorunluluğu, Kanunun 5 ve 6. maddelerin |
| e35 | Silme ve yok etme işlemlerine ilişkin kayıtlar en az kaç yıl saklanır? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e37 | Açık rızaya dayanan işlemede aydınlatma ile açık rıza birlikte alınabilir mi? | ✗ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e39 | İnternet sitesinde reklam çerezlerinin açık rıza alınmadan kullanılması hakkında Kurul hangi yaptırımı uygulamıştır? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e42 | İşyerindeki kameraların konumu hakkında Kurul işverene ne talimat vermiştir? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e49 | Ciddi ve yakın tehlike nedeniyle çalışmaktan kaçınan çalışanın o dönemdeki ücreti ne olur? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
