# Değerlendirme — openrouter:deepseek/deepseek-v4.1-flash-1017

Tarih: 2026-11-13 20:33 | commit: ca327a3 | eşik: 0.637 | reranker: açık | soru: 56 (50 kapsam içi, 6 kapsam dışı) | hata: 0

Beklenen cevaplar resmî metinle elle doğrulandı (74/74; geliştirici kontrolü, hukukçu incelemesi değildir) (2026-11-17). `icerik` anahtar kelime eşleşmesidir; kesin doğruluk için ham cevaplar elle okunmalı.

## Kapsam içi

| Ölçüt | Tümü | Mevzuat | Karar |
|---|---|---|---|
| Beklenen kaynak bağlamda | 47/50 (%94) | 38/41 (%93) | 9/9 (%100) |
| Beklenen kaynağa atıf | 41/50 (%82) | 34/41 (%83) | 7/9 (%78) |
| Cevap içeriği (anahtar) | 42/50 (%84) | 36/41 (%88) | 6/9 (%67) |
| **Doğru (cevap + atıf + içerik)** | 40/50 (%80) | 34/41 (%83) | 6/9 (%67) |
| Yanlış "bilmiyorum" | 7/50 (%14) | 5/41 (%12) | 2/9 (%22) |

Yanlış "bilmiyorum" katmanları: {'arama_esigi': 7}

## Kapsam dışı

Doğru "bilmiyorum": 6/6 (%100) — katmanlar: {'arama_esigi': 6}

## Diğer

Geçersiz atıf (bağlamda olmayan [n]): 0 | süre medyan 3.66 sn, en uzun 29.9 sn

## Başarısız sorular

| # | Soru | Bağlam | Atıf | İçerik | Not |
|---|---|---|---|---|---|
| e02 | İş güvencesi hükümlerinden yararlanmak için işyerinde en az kaç işçi çalışıyor olmalı? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e13 | Günlük çalışma süresi en fazla kaç saat olabilir? | ✗ | ✗ | ✓ | Günlük çalışma süresi her ne şekilde olursa olsun 11 saati aşamaz [1]. Telafi çalışmaları da günlük en çok çal |
| e24 | Denkleştirme hangi süre içinde tamamlanmalıdır? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e25 | KVKK'ya göre açık rıza nasıl tanımlanır? | ✗ | ✗ | ✓ | Açık rıza, Kanun'un tanımlar maddesinde "belirli bir konuya ilişkin, bilgilendirilmeye dayanan ve özgür iradey |
| e35 | Silme ve yok etme işlemlerine ilişkin kayıtlar en az kaç yıl saklanır? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e37 | Açık rızaya dayanan işlemede aydınlatma ile açık rıza birlikte alınabilir mi? | ✗ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e38 | İşveren, işten çıkardığı çalışanı şirketin sosyal medya hesabından duyurursa Kurul ne karar vermiştir? | ✓ | ✓ | ✗ | Kurul, 2022/386 sayılı kararında, iş akdi sonlandırılan ilgili kişinin açık ad-soyadı ve hakkındaki ithamları  |
| e39 | İnternet sitesinde reklam çerezlerinin açık rıza alınmadan kullanılması hakkında Kurul hangi yaptırımı uygulamıştır? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e42 | İşyerindeki kameraların konumu hakkında Kurul işverene ne talimat vermiştir? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
| e49 | Ciddi ve yakın tehlike nedeniyle çalışmaktan kaçınan çalışanın o dönemdeki ücreti ne olur? | ✓ | ✗ | ✗ | bilmiyorum (arama_esigi) |
