# İlişkiler ve Değişiklik Geçmişi Örneklemi (seed=5, 15 madde)

Yöntem: `articles.jsonl` içindeki 350 madde anahtarının sıralı listesinden (`sorted(keys)`) `random.seed(5)` ile seçilen 15 madde kaynak metinleri, `degisiklik_notlari` ve `dipnotlar` alanlarıyla tek tek karşılaştırılmıştır.

## Özet (Önce vs Sonra)

| Metrik | İlk çalıştırma (Önce) | Düzeltme sonrası (Sonra) |
| --- | --- | --- |
| Toplam madde | 350 | 350 |
| Geçmişli madde / kayıt | 123 / 217 | 123 / 218 |
| Tarihsiz atlanan | 1 | 0 |
| Yönlü ilişki (`atif_yapar`) | 292 (216 madde) | 317 (223 madde) |
| `seed=5` örneklem doğruluğu | 12 / 15 doğru (%80,0) | 15 / 15 doğru (%100,0) |

İlk çalıştırmada `seed=5` örnekleminde yakalanan ve `src/ingest/iliskiler.py` içinde düzeltilen 3 sorun:
1. `#3 (is-kanunu:98)`: `isg-kanunu:37` fıkra 2 içindeki `"4857 sayılı Kanunun 4 üncü maddesinin ... ile 98 inci maddesinin ..."` aynı cümle içi atıfı ilk sürümde `isg-kanunu:37 -> is-kanunu:98` kenarını kaçırmıştı; aynı cümlede adlandırılmış belge mirası eklenince `atif_alir -> isg-kanunu:37` eklendi (ayrıca dipnotta `"çıkartılmıştır"` kalıbı `"Yürürlükten kaldırma"` olarak sınıflandırıldı).
2. `#4 (yurtdisi-aktarim-yon:11)`: `"d) Kişisel verileri aktarılan ilgili kişilerin Kanunun 11 inci maddesinde..."` cümlesinde `RE_HARICI_BELGE_ADI`, büyük harfle başlayan `"Kişisel ... Kanunun"` öbeğini yanlışlıkla özel kanun adı sandığı için `kvkk:11` atlanmıştı; Title-Case kuralıyla `kvkk:11` kurtarıldı.
3. `#7 (isg-kanunu:7)`: `isg-kanunu:32` maddesindeki `"22/5/2003 tarihli ve 4857 sayılı İş Kanununun;\na) 7 nci..."` çok satırlı bent listesi `\n` sınırında sıfırlandığı için yanlışlıkla `isg-kanunu:32 -> isg-kanunu:7` (yanlış pozitif) üretmişti; bent başlığı belge takibiyle `is-kanunu:7` olarak düzeltildi.

*(Ek bulgu: `is-kanunu-1475:14` 5 no'lu dipnottaki `"9/8/2002 tarihli ve 4773 sayılı Kanunla ..."` kaydı madde numarası içermediği için ilk çalıştırmada `tarihsiz atlanan=1` olarak atlanmıştı; `RE_DIPNOT_KANUN_GENEL` ile `"4773 s. Kanun"` olarak alındı ve `tarihsiz atlanan` 0'a indi.)*

## 15 Maddelik Doğrulama Tablosu (`seed=5`, Sonra)

| # | Madde Anahtarı | Başlık | Geçmiş (Sonra) | İlişkili (Sonra) | Önce -> Sonra Durumu | Not |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `yillik-izin-yon:19` | Yıllık İzin Çizelgelerinin Hazırlanması ve İlanı | 0 | `[]` | Doğru -> Doğru | Not/dipnot/madde atfı yok |
| 2 | `is-kanunu:5` | Eşit davranma ilkesi | 1 (`2014-02-06`, `6518 s. Kanun md. 57`, `Ek`) | `atif_yapar: is-kanunu:20`; `atif_alir: is-kanunu:99` | Doğru -> Doğru | `2821 s. Kanunun 31.` harici olduğundan doğru elendi; `20.` doğru alındı |
| 3 | `is-kanunu:98` | İşyerini bildirme yükümlülüğüne aykırılık | 2 (`2008-05-15` `5763/8`; `2012-06-20` `6331/37` `Yürürlükten kaldırma`) | `atif_yapar: is-kanunu:3`; `atif_alir: isg-kanunu:37` | Sorunlu -> Doğru | `isg-kanunu:37` f2'deki `98 inci` atfı düzeltme sonrası eklendi |
| 4 | `yurtdisi-aktarim-yon:11` | Uluslararası sözleşme niteliğinde olmayan anlaşmayla uygun güvencenin sağlanması | 0 | `atif_yapar: kvkk:4, kvkk:11` | Sorunlu -> Doğru | `(3)(d)`'deki `"ilgili kişilerin Kanunun 11 inci maddesinde"` düzeltme sonrası eklendi |
| 5 | `kvkk:27` | Personele ve özlük haklarına ilişkin hükümler | 1 (`2017-11-28`, `7061 s. Kanun md. 119`, `İbare/hüküm eklenmesi`) | `[]` | Doğru -> Doğru | `657`, `375 s. KHK`, `5510` harici olduğundan atlandı |
| 6 | `basvuru-teblig:7` | Ücret | 0 | `atif_alir: basvuru-teblig:6` | Doğru -> Doğru | `6.` maddeden `"7 nci maddede belirtilen ücret"` atfı doğru eşleşti |
| 7 | `isg-kanunu:7` | İş sağlığı ve güvenliği hizmetlerinin desteklenmesi | 1 (`2018-07-02`, `703 s. KHK md. 210`, `İbare/hüküm değişikliği`) | `atif_alir: isg-kanunu:38` | Sorunlu (FP) -> Doğru | İlk çalıştırmadaki yanlış `isg-kanunu:32` kenarı kaldırıldı |
| 8 | `is-kanunu:47` | Genel tatil ücreti | 0 | `atif_alir: is-kanunu:44, is-kanunu:49` | Doğru -> Doğru | `49.` maddedeki `"46, 47 ve 48 inci maddenin"` aralığı/listesi doğru çözüldü |
| 9 | `yurtdisi-aktarim-yon:10` | Uygun güvence sağlama yolları | 0 | `atif_yapar: kvkk:5, kvkk:6`; `atif_alir: yurtdisi-aktarim-yon:6, yurtdisi-aktarim-yon:16` | Doğru -> Doğru | Yönetmelikteki `"Kanunun 5 inci ve 6 ncı"` dayanakla `kvkk`'ya bağlandı |
| 10 | `calisma-sureleri-yon:6` | Kısmi Süreli Çalışma | 0 | `[]` | Doğru -> Doğru | Madde atfı/değişiklik yok |
| 11 | `is-kanunu:114` | Üçlü Danışma Kurulu | 0 | `[]` | Doğru -> Doğru | Madde atfı/değişiklik yok |
| 12 | `is-kanunu-1475:1` | *(Başlık alanı kanun künyesi)* | 1 (`2003-05-22`, `4857 s. Kanun md. 120`, `Mülga`) | `[]` | Doğru -> Doğru | `(Mülga: 22/5/2003/4857/120 md.)` eğik çizgili tarih/sayı doğru ayrıştırıldı |
| 13 | `is-kanunu:Geçici 11` | *(Başlıksız geçici madde)* | 2 (`2020-07-23` `7252/6`; `2023-11-08` `AYM E.2020/75, K.2023/188`) | `[]` | Doğru -> Doğru | AYM dipnotu ve `3213 s. Kanun` harici ayrımı doğru |
| 14 | `isg-kanunu:9` | Tehlike sınıfının belirlenmesi | 0 | `atif_alir: isg-kanunu:38` | Doğru -> Doğru | `5510/83` harici elendi; `38.` maddeden gelen yürürlük atfı doğru |
| 15 | `is-kanunu:46` | Hafta tatili ücreti | 2 (`2015-04-04` `6645/35`; `2025-07-10` `7553/9`) | `atif_yapar: is-kanunu:24, 25, 63, Ek 2`; `atif_alir: is-kanunu:49` | Doğru -> Doğru | `24 ve 25 inci maddelerin`, `63 üncü`, `Ek 2 nci` ve gelen `49.` tam doğru |
