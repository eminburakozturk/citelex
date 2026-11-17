# Değerlendirme — openrouter:deepseek/deepseek-v4.1-flash-1017

Tarih: 2026-11-14 00:02 | commit: 2f828ba | eşik: 0.637 | reranker: açık | soru: 56 (50 kapsam içi, 6 kapsam dışı) | hata: 0

Beklenen cevaplar resmî metinle elle doğrulandı (74/74; geliştirici kontrolü, hukukçu incelemesi değildir) (2026-11-17). `icerik` anahtar kelime eşleşmesidir; kesin doğruluk için ham cevaplar elle okunmalı.

## Kapsam içi

| Ölçüt | Tümü | Mevzuat | Karar |
|---|---|---|---|
| Beklenen kaynak bağlamda | 46/50 (%92) | 37/41 (%90) | 9/9 (%100) |
| Beklenen kaynağa atıf | 46/50 (%92) | 37/41 (%90) | 9/9 (%100) |
| Cevap içeriği (anahtar) | 49/50 (%98) | 41/41 (%100) | 8/9 (%89) |
| **Doğru (cevap + atıf + içerik)** | 45/50 (%90) | 37/41 (%90) | 8/9 (%89) |
| Yanlış "bilmiyorum" | 0/50 (%0) | 0/41 (%0) | 0/9 (%0) |

Yanlış "bilmiyorum" katmanları: —

## Kapsam dışı

Doğru "bilmiyorum": 5/6 (%83) — katmanlar: {'llm': 5}

## Diğer

Geçersiz atıf (bağlamda olmayan [n]): 0 | süre medyan 5.47 sn, en uzun 44.88 sn

## Başarısız sorular

| # | Soru | Bağlam | Atıf | İçerik | Not |
|---|---|---|---|---|---|
| e13 | Günlük çalışma süresi en fazla kaç saat olabilir? | ✗ | ✗ | ✓ | Günlük çalışma süresi her ne şekilde olursa olsun 11 saati aşamaz [1]. Telafi çalışmaları da günlük en çok çal |
| e25 | KVKK'ya göre açık rıza nasıl tanımlanır? | ✗ | ✗ | ✓ | Açık rıza, Kanun'un tanımlar maddesinde "belirli bir konuya ilişkin, bilgilendirilmeye dayanan ve özgür iradey |
| e35 | Silme ve yok etme işlemlerine ilişkin kayıtlar en az kaç yıl saklanır? | ✗ | ✗ | ✓ | CEVAP: 2022/172 sayılı Kurul kararında, Kişisel Verilerin Silinmesi, Yok Edilmesi veya Anonim Hale Getirilmesi |
| e37 | Açık rızaya dayanan işlemede aydınlatma ile açık rıza birlikte alınabilir mi? | ✗ | ✗ | ✓ | Hayır, birlikte alınamaz; aydınlatma yükümlülüğü ile açık rıza alınması işlemlerinin ayrı ayrı yerine getirilm |
| e38 | İşveren, işten çıkardığı çalışanı şirketin sosyal medya hesabından duyurursa Kurul ne karar vermiştir? | ✓ | ✓ | ✗ | Kurul, 2022/386 sayılı kararında, iş akdi sonlandırılan ilgili kişinin açık ad-soyadı ve hakkındaki ithamları  |
| d03 | İş mahkemesinde dava açmadan önce arabuluculuk görüşmeleri en fazla kaç hafta sürer? | — | — | — | CEVAP VERDİ: İş mahkemesinde dava şartı arabuluculukta arabulucu, yapılan başvuruyu görevlendirildiği tarihten itibaren üç  |
