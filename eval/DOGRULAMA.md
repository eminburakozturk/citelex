# Değerlendirme seti doğrulama listesi

Her soruda: resmî metni aç, beklenen kaynakta kanıt cümlesinin geçtiğini ve sorunun bu maddeyle cevaplandığını kontrol et.
Doğruysa `[ ]` kutusunu `[x]` yap. Yanlış/eksikse `Not:` satırına yaz (ör. "m.17 de beklenmeli", "soru belirsiz").
Kapsam dışı sorularda: derlemde (KVKK, İş Kanunu, İSG ve ilgili yönetmelik/tebliğler, seçili Kurul kararları) cevabı
OLMADIĞINI kontrol et. Bitince: `python -m scripts.dogrulama_listesi --oku`

## Ana değerlendirme seti (56 soru)

### e01 — Hangi iş sözleşmelerinin yazılı yapılması zorunludur?
- Beklenen kaynak: `is-kanunu:8` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > İş sözleşmesi, bir tarafın (işçi) bağımlı olarak iş görmeyi, diğer tarafın (işveren) da ücret ödemeyi üstlenmesinden oluşan sözleşmedir. İş sözleşmesi, Kanunda aksi belirtilmedikçe, özel bir şekle tâbi değildir. Süresi bir yıl ve daha fazla olan iş sözleşmelerinin yazılı şekilde yapılması zorunludur. Bu belgeler damga vergisi ve her çeşit resim ve harçtan muaftır. Yazılı sözleşme yapılmayan hallerde işveren işçiye en geç iki ay içinde genel ve özel çalışma koşullarını, günlük ya da …
- Cevapta aranan: (bir yıl | 1 yıl) VE (yazılı)
- [x] Doğrulandı
- Not: 

### e02 — İş güvencesi hükümlerinden yararlanmak için işyerinde en az kaç işçi çalışıyor olmalı?
- Beklenen kaynak: `is-kanunu:18` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > Otuz veya daha fazla işçi çalıştıran işyerlerinde en az altı aylık kıdemi olan işçinin belirsiz süreli iş sözleşmesini fesheden işveren, işçinin yeterliliğinden veya davranışlarından ya da işletmenin, işyerinin veya işin gereklerinden kaynaklanan geçerli bir sebebe dayanmak …
- Cevapta aranan: (otuz | 30)
- [x] Doğrulandı
- Not: 

### e03 — İşe iade başvurusu sonrası işveren işçiyi işe başlatmazsa ne kadar tazminat öder?
- Beklenen kaynak: `is-kanunu:21` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … sebebin geçerli olmadığı mahkemece veya özel hakem tarafından tespit edilerek feshin geçersizliğine karar verildiğinde, işveren, işçiyi bir ay içinde işe başlatmak zorundadır. İşçiyi başvurusu üzerine işveren bir ay içinde işe başlatmaz ise, işçiye en az dört aylık ve en çok sekiz aylık ücreti tutarında tazminat ödemekle yükümlü olur. Mahkeme veya özel hakem feshin geçersizliğine karar verdiğinde, işçinin işe başlatılmaması halinde ödenecek tazminat miktarını da belirler. Kararın kesinleşmesine kadar …
- Cevapta aranan: (dört | 4) VE (sekiz | 8)
- [x] Doğrulandı
- Not: 

### e04 — Ücret en geç ne sıklıkla ödenmek zorundadır?
- Beklenen kaynak: `is-kanunu:32` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … esaslar anılan bakanlıklarca müştereken çıkarılacak yönetmelikle düzenlenir. Emre muharrer senetle (bono ile), kuponla veya yurtta geçerli parayı temsil ettiği iddia olunan bir senetle veya diğer herhangi bir şekilde ücret ödemesi yapılamaz. Ücret en geç ayda bir ödenir. İş sözleşmeleri veya toplu iş sözleşmeleri ile ödeme süresi bir haftaya kadar indirilebilir. İş sözleşmelerinin sona ermesinde, işçinin ücreti ile sözleşme ve Kanundan doğan para ile ölçülmesi mümkün menfaatlerinin tam olarak ödenmesi …
- Cevapta aranan: (ayda bir)
- [x] Doğrulandı
- Not: 

### e05 — Ücreti kaç gün ödenmeyen işçi çalışmaktan kaçınabilir?
- Beklenen kaynak: `is-kanunu:34` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > Ücreti ödeme gününden itibaren yirmi gün içinde mücbir bir neden dışında ödenmeyen işçi, iş görme borcunu yerine getirmekten kaçınabilir. Bu nedenle kişisel kararlarına dayanarak iş görme borcunu yerine getirmemeleri sayısal olarak toplu bir nitelik kazansa dahi grev olarak nitelendirilemez. …
- Cevapta aranan: (yirmi | 20)
- [x] Doğrulandı
- Not: 

### e06 — İşveren bir ayda işçinin ücretinden ceza olarak en fazla ne kadar kesinti yapabilir?
- Beklenen kaynak: `is-kanunu:38` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … gösterilmiş olan sebepler dışında işçiye ücret kesme cezası veremez. İşçi ücretlerinden ceza olarak yapılacak kesintilerin işçiye derhal sebepleriyle beraber bildirilmesi gerekir. İşçi ücretlerinden bu yolda yapılacak kesintiler bir ayda iki gündelikten veya parça başına yahut yapılan iş miktarına göre verilen ücretlerde işçinin iki günlük kazancından fazla olamaz. Bu paralar işçilerin eğitimi ve sosyal hizmetleri için kullanılıp harcanmak üzere Çalışma ve Sosyal Güvenlik Bakanlığı hesabına …
- Cevapta aranan: (iki gündelik | iki günlük | 2 gündelik | 2 günlük)
- [x] Doğrulandı
- Not: 

### e07 — Bir yılda en fazla kaç saat fazla çalışma yaptırılabilir?
- Beklenen kaynak: `is-kanunu:41` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5)), `fazla-calisma-yon:5` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6249&MevzuatTur=7&MevzuatTertip=5))
- Kanıt (derlemden): > … yazılı sağlık nedenlerine dayanan kısa veya sınırlı süreli işlerde ve 69 uncu maddede belirtilen gece çalışmasında fazla çalışma yapılamaz. Fazla saatlerle çalışmak için işçinin onayının alınması gerekir. Fazla çalışma süresinin toplamı bir yılda ikiyüzyetmiş saatten fazla olamaz. (Ek fıkra: 10/9/2014-6552/4 md.) Bu Kanunun 42 nci ve 43 üncü maddelerinde sayılan hâller dışında yer altında maden işlerinde çalışan işçilere fazla çalışma yaptırılamaz. (Ek fıkra: 10/9/2014-6552/4 md.) Yer altında maden …
- Cevapta aranan: (ikiyüzyetmiş | iki yüz yetmiş | 270)
- [x] Doğrulandı
- Not: 

### e08 — Fazla çalışma karşılığında ücret yerine serbest zaman kullanılırsa her saat için ne kadar süre verilir?
- Beklenen kaynak: `is-kanunu:41` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5)), `fazla-calisma-yon:6` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6249&MevzuatTur=7&MevzuatTertip=5))
- Kanıt (derlemden): > … ücret normal çalışma ücretinin saat başına düşen miktarının yüzde yirmibeş yükseltilmesiyle ödenir. Fazla çalışma veya fazla sürelerle çalışma yapan işçi isterse, bu çalışmalar karşılığı zamlı ücret yerine, fazla çalıştığı her saat karşılığında bir saat otuz dakikayı, fazla sürelerle çalıştığı her saat karşılığında bir saat onbeş dakikayı serbest zaman olarak kullanabilir. İşçi hak ettiği serbest zamanı altı ay zarfında, çalışma süreleri içinde ve ücretinde bir kesinti olmadan kullanır. 63 üncü maddenin son …
- Cevapta aranan: (bir saat otuz dakika | 1 saat 30 dakika | 1,5 saat | bir buçuk saat)
- [x] Doğrulandı
- Not: 

### e09 — Hafta tatili en az kaç saat olmalıdır?
- Beklenen kaynak: `is-kanunu:46` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > Bu Kanun kapsamına giren işyerlerinde, işçilere tatil gününden önce 63 üncü maddeye göre belirlenen iş günlerinde çalışmış olmaları koşulu ile yedi günlük bir zaman dilimi içinde kesintisiz en az yirmidört saat dinlenme (hafta tatili) verilir. (Ek cümleler:10/7/2025-7553/9 md.) Ancak Kültür ve Turizm Bakanlığı tarafından turizm işletmesi belgesi verilen konaklama tesislerinde çalışan işçilerin bu fıkra kapsamında hak kazandığı hafta tatili, işçinin yazılı …
- Cevapta aranan: (yirmidört | yirmi dört | 24)
- [x] Doğrulandı
- Not: 

### e10 — On beş yıl ve daha fazla kıdemi olan işçinin yıllık ücretli izni en az kaç gündür?
- Beklenen kaynak: `is-kanunu:53` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5)), `yillik-izin-yon:9` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=5451&MevzuatTur=7&MevzuatTertip=5))
- Kanıt (derlemden): > … uygulanmaz. İşçilere verilecek yıllık ücretli izin süresi, hizmet süresi; a) Bir yıldan beş yıla kadar (beş yıl dahil) olanlara ondört günden, b) Beş yıldan fazla onbeş yıldan az olanlara yirmi günden, c) Onbeş yıl (dahil) ve daha fazla olanlara yirmialtı günden, Az olamaz. (Ek cümle: 10/9/2014-6552/5 md.) Yer altı işlerinde çalışan işçilerin yıllık ücretli izin süreleri dörder gün arttırılarak uygulanır. Ancak onsekiz ve daha küçük yaştaki işçilerle elli ve daha yukarı yaştaki işçilere verilecek …
- Cevapta aranan: (yirmialtı | yirmi altı | 26)
- [x] Doğrulandı
- Not: 

### e11 — Yıllık izin bölünerek kullanılırsa bölümlerden biri en az kaç gün olmalıdır?
- Beklenen kaynak: `is-kanunu:56` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5)), `yillik-izin-yon:6` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=5451&MevzuatTur=7&MevzuatTertip=5))
- Kanıt (derlemden): > … Bu iznin 53 üncü maddede gösterilen süreler içinde işveren tarafından sürekli bir şekilde verilmesi zorunludur. (Değişik üçüncü fıkra: 14/4/2016-6704/16 md.) Ancak, 53 üncü maddede öngörülen izin süreleri, tarafların anlaşması ile bir bölümü on günden aşağı olmamak üzere bölümler hâlinde kullanılabilir. İşveren tarafından yıl içinde verilmiş bulunan diğer ücretli ve ücretsiz izinler veya dinlenme ve hastalık izinleri yıllık izne mahsup edilemez. Yıllık ücretli izin günlerinin hesabında izin süresine …
- Cevapta aranan: (on gün | 10 gün)
- [x] Doğrulandı
- Not: 

### e12 — Yıllık iznini başka şehirde geçirecek işçiye kaç güne kadar yol izni verilir?
- Beklenen kaynak: `is-kanunu:56` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5)), `yillik-izin-yon:6` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=5451&MevzuatTur=7&MevzuatTertip=5))
- Kanıt (derlemden): > … süresinden sayılmaz. Yıllık ücretli izinleri işyerinin kurulu bulunduğu yerden başka bir yerde geçirecek olanlara istemde bulunmaları ve bu hususu belgelemeleri koşulu ile gidiş ve dönüşlerinde yolda geçecek süreleri karşılamak üzere işveren toplam dört güne kadar ücretsiz izin vermek zorundadır. İşveren, işyerinde çalışan işçilerin yıllık ücretli izinlerini gösterir izin kayıt belgesi tutmak zorundadır. (Ek fıkra: 10/9/2014-6552/6 md.) Alt işveren işçilerinden, alt işvereni değiştiği hâlde aynı işyerinde …
- Cevapta aranan: (dört | 4)
- [x] Doğrulandı
- Not: 

### e13 — Günlük çalışma süresi en fazla kaç saat olabilir?
- Beklenen kaynak: `is-kanunu:63` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5)), `calisma-sureleri-yon:5` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=5447&MevzuatTur=7&MevzuatTertip=5))
- Kanıt (derlemden): > … md.) Yer altı maden işlerinde çalışan işçilerin çalışma süresi; günde en çok yedi buçuk, haftada en çok otuz yedi buçuk saattir. Tarafların anlaşması ile haftalık normal çalışma süresi, işyerlerinde haftanın çalışılan günlerine, günde onbir saati aşmamak koşulu ile farklı şekilde dağıtılabilir. Bu halde, iki aylık süre içinde işçinin haftalık ortalama çalışma süresi, normal haftalık çalışma süresini aşamaz. Denkleştirme süresi toplu iş sözleşmeleri ile dört aya kadar artırılabilir. (Ek …
- Cevapta aranan: (onbir | on bir | 11)
- [x] Doğrulandı
- Not: 

### e14 — Yedi buçuk saatten uzun süren işlerde ara dinlenmesi ne kadardır?
- Beklenen kaynak: `is-kanunu:68` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … bir zamanında o yerin gelenekleri ve işin gereğine göre ayarlanmak suretiyle işçilere; a) Dört saat veya daha kısa süreli işlerde onbeş dakika, b) Dört saatten fazla ve yedibuçuk saate kadar (yedibuçuk saat dahil) süreli işlerde yarım saat, c) Yedibuçuk saatten fazla süreli işlerde bir saat, ara dinlenmesi verilir. Bu dinlenme süreleri en az olup aralıksız verilir. Ancak bu süreler, iklim, mevsim, o yerdeki gelenekler ve işin niteliği göz önünde tutularak sözleşmeler ile aralı olarak kullandırılabilir. Dinlenmeler bir işyerinde …
- Cevapta aranan: (bir saat | 1 saat)
- [x] Doğrulandı
- Not: 

### e15 — Kadın işçinin doğum izni toplam kaç haftadır?
- Beklenen kaynak: `is-kanunu:74` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > Kadın işçilerin doğumdan önce sekiz ve doğumdan sonra onaltı hafta olmak üzere toplam yirmidört haftalık süre için çalıştırılmamaları esastır. Çoğul gebelik halinde doğumdan önce çalıştırılmayacak sekiz haftalık süreye iki hafta süre eklenir. Ancak, sağlık durumu uygun olduğu takdirde, doktorun onayı ile kadın işçi isterse doğumdan önceki iki haftaya …
- Cevapta aranan: (yirmidört | yirmi dört | 24)
- [x] Doğrulandı
- Not: 

### e16 — Özel sektör işyerinde kaç işçiden itibaren ve yüzde kaç oranında engelli çalıştırmak zorunludur?
- Beklenen kaynak: `is-kanunu:30` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > İşverenler, elli veya daha fazla işçi çalıştırdıkları özel sektör işyerlerinde yüzde üç engelli, kamu işyerlerinde ise yüzde dört engelli ve yüzde iki eski hükümlü işçiyi veya 21/6/1927 tarihli ve 1111 sayılı Askerlik Kanunu veya 16/6/1927 tarihli ve 1076 sayılı Yedek Subaylar ve Yedek Askeri Memurlar Kanunu kapsamına giren ve askerlik …
- Cevapta aranan: (elli | 50) VE (yüzde üç | %3 | % 3)
- [x] Doğrulandı
- Not: 

### e17 — Eşit davranma ilkesine aykırılık halinde işçi ne kadar tazminat isteyebilir?
- Beklenen kaynak: `is-kanunu:5` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … daha düşük ücret kararlaştırılamaz. İşçinin cinsiyeti nedeniyle özel koruyucu hükümlerin uygulanması, daha düşük bir ücretin uygulanmasını haklı kılmaz. İş ilişkisinde veya sona ermesinde yukarıdaki fıkra hükümlerine aykırı davranıldığında işçi, dört aya kadar ücreti tutarındaki uygun bir tazminattan başka yoksun bırakıldığı haklarını da talep edebilir. 2821 sayılı Sendikalar Kanununun 31 inci maddesi hükümleri saklıdır. 20 nci madde hükümleri saklı kalmak üzere işverenin yukarıdaki fıkra hükümlerine aykırı …
- Cevapta aranan: (dört ay | 4 ay)
- [x] Doğrulandı
- Not: 

### e18 — Bildirim süresi içinde yeni iş arama izni günde en az kaç saattir?
- Beklenen kaynak: `is-kanunu:27` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > Bildirim süreleri içinde işveren, işçiye yeni bir iş bulması için gerekli olan iş arama iznini iş saatleri içinde ve ücret kesintisi yapmadan vermeye mecburdur. İş arama izninin süresi günde iki saatten az olamaz ve işçi isterse iş arama izin saatlerini birleştirerek toplu kullanabilir. Ancak iş arama iznini toplu kullanmak isteyen işçi, bunu işten ayrılacağı günden evvelki günlere rastlatmak ve bu durumu işverene bildirmek zorundadır. İşveren yeni …
- Cevapta aranan: (iki saat | 2 saat)
- [x] Doğrulandı
- Not: 

### e19 — Kıdem tazminatı her tam yıl için kaç günlük ücret üzerinden ödenir?
- Beklenen kaynak: `is-kanunu-1475:14` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=1475&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … nedeniyle, Feshedilmesi veya kadının evlendiği tarihten itibaren bir yıl içerisinde kendi arzusu ile sona erdirmesi veya işçinin ölümü sebebiyle son bulması hallerinde işçinin işe başladığı tarihten itibaren hizmet aktinin devamı süresince her geçen tam yıl için işverence işçiye 30 günlük ücreti tutarında kıdem tazminatı ödenir. Bir yıldan artan süreler için de aynı oran üzerinden ödeme yapılır. (Değişik fıkralar: 17/10/1980 - 2320/1 md.): İşçilerin kıdemleri, hizmet akdinin devam etmiş veya fasılalarla …
- Cevapta aranan: (30 | otuz)
- [x] Doğrulandı
- Not: 

### e20 — İşe iade için arabulucuya başvuru süresi ne kadardır?
- Beklenen kaynak: `is-kanunu:20` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > (Değişik birinci fıkra: 12/10/2017-7036/11 md.) İş sözleşmesi feshedilen işçi, fesih bildiriminde sebep gösterilmediği veya gösterilen sebebin geçerli bir sebep olmadığı iddiası ile fesih bildiriminin tebliği tarihinden itibaren bir ay içinde işe iade talebiyle, İş Mahkemeleri Kanunu hükümleri uyarınca arabulucuya başvurmak zorundadır. Arabuluculuk faaliyeti sonunda anlaşmaya varılamaması hâlinde, son tutanağın düzenlendiği tarihten itibaren, iki hafta içinde iş mahkemesinde dava …
- Cevapta aranan: (bir ay | 1 ay)
- [x] Doğrulandı
- Not: 

### e21 — İzin kurulu hangi büyüklükteki işyerlerinde kurulur ve kaç kişiden oluşur?
- Beklenen kaynak: `yillik-izin-yon:15` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=5451&MevzuatTur=7&MevzuatTertip=5))
- Kanıt (derlemden): > İşçi sayısı yüzden fazla olan işyerlerinde işveren veya işveren vekilini temsilen bir, işçileri temsilen iki kişi olmak üzere toplam üç kişiden oluşan izin kurulu kurulur. Kurula işveren temsilcisi başkanlık eder. Kurulun başkanı dışında kalan işçi üyeleri ve yedekleri …
- Cevapta aranan: (yüz | 100) VE (üç kişi | 3 kişi)
- [x] Doğrulandı
- Not: 

### e22 — İşçi yıllık izin talebini ne kadar önceden işverene bildirmelidir?
- Beklenen kaynak: `yillik-izin-yon:7` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=5451&MevzuatTur=7&MevzuatTertip=5))
- Kanıt (derlemden): > İşçi yukarıdaki maddelere göre hak ettiği yıllık ücretli iznini, kullanmak istediği zamandan en az bir ay önce işverene yazılı olarak bildirir. İşveren veya işveren vekilleri, bu istekleri Yönetmeliğin 15 inci maddesinde sözü geçen izin kuruluna veya 18 inci maddesinde belirtilen kişilere bildirir.
- Cevapta aranan: (bir ay | 1 ay)
- [x] Doğrulandı
- Not: 

### e23 — Fazla çalışma yaptırmak için işçiden ne alınması gerekir?
- Beklenen kaynak: `fazla-calisma-yon:9` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6249&MevzuatTur=7&MevzuatTertip=5))
- Kanıt (derlemden): > Fazla çalışma ve fazla sürelerle çalışma yaptırmak için işçinin yazılı onayının alınması gerekir. Zorunlu nedenlerle veya olağanüstü durumlarda yapılan fazla çalışma ve fazla sürelerle çalışma için bu onay aranmaz. (Değişik:RG-25/8/2017-30165) Fazla çalışma ihtiyacı olan işverence bu onay iş sözleşmesinin yapılması esnasında ya da bu …
- Cevapta aranan: (yazılı onay)
- [x] Doğrulandı
- Not: 

### e24 — Denkleştirme hangi süre içinde tamamlanmalıdır?
- Beklenen kaynak: `calisma-sureleri-yon:5` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=5447&MevzuatTur=7&MevzuatTertip=5)), `is-kanunu:63` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4857&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … şekilde dağıtılabilir. Bu halde, yoğunlaştırılmış iş haftası veya haftalarından sonraki dönemde işçinin daha az sürelerle çalıştırılması suretiyle, toplam çalışma süresi, çalışması gereken toplam normal süreyi geçmeyecek şekilde denkleştirilir. Denkleştirme iki aylık süre içinde tamamlanacak, bu süre toplu iş sözleşmeleri ile dört aya kadar artırılabilecektir.(Ek cümle:RG-25/8/2017- 30165)Turizm sektöründe dört aylık süre içinde işçinin haftalık ortalama çalışma süresi, normal haftalık çalışma süresini aşamaz; …
- Cevapta aranan: (iki ay | 2 ay)
- [x] Doğrulandı
- Not: 

### e25 — KVKK'ya göre açık rıza nasıl tanımlanır?
- Beklenen kaynak: `kvkk:3` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6698&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > (1) Bu Kanunun uygulanmasında; a) Açık rıza: Belirli bir konuya ilişkin, bilgilendirilmeye dayanan ve özgür iradeyle açıklanan rızayı, b) Anonim hâle getirme: Kişisel verilerin, başka verilerle eşleştirilerek dahi hiçbir surette kimliği belirli veya belirlenebilir bir gerçek kişiyle ilişkilendirilemeyecek hâle getirilmesini, c) Başkan: Kişisel Verileri Koruma …
- Cevapta aranan: (özgür irade) VE (bilgilendir)
- [x] Doğrulandı
- Not: 

### e26 — Kişisel verilerin işlenmesinde amaçla ilgili genel ilke nedir?
- Beklenen kaynak: `kvkk:4` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6698&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … işlenebilir. (2) Kişisel verilerin işlenmesinde aşağıdaki ilkelere uyulması zorunludur: a) Hukuka ve dürüstlük kurallarına uygun olma. b) Doğru ve gerektiğinde güncel olma. c) Belirli, açık ve meşru amaçlar için işlenme. ç) İşlendikleri amaçla bağlantılı, sınırlı ve ölçülü olma. d) İlgili mevzuatta öngörülen veya işlendikleri amaç için gerekli olan süre kadar muhafaza edilme.
- Cevapta aranan: (ölçülü) VE (sınırlı)
- [x] Doğrulandı
- Not: 

### e27 — Kişisel veriler hangi durumda silinmek, yok edilmek veya anonim hale getirilmek zorundadır?
- Beklenen kaynak: `kvkk:7` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6698&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > (1) Bu Kanun ve ilgili diğer kanun hükümlerine uygun olarak işlenmiş olmasına rağmen, işlenmesini gerektiren sebeplerin ortadan kalkması hâlinde kişisel veriler resen veya ilgili kişinin talebi üzerine veri sorumlusu tarafından silinir, yok edilir veya anonim hâle getirilir. (2) Kişisel verilerin silinmesi, yok edilmesi veya anonim hâle getirilmesine ilişkin diğer kanunlarda yer …
- Cevapta aranan: (sebeplerin ortadan kalk | sebepler ortadan kalk)
- [x] Doğrulandı
- Not: 

### e28 — Kişisel veriler başkalarınca hukuka aykırı elde edilirse veri sorumlusu kime ve ne zaman bildirir?
- Beklenen kaynak: `kvkk:12` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6698&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … başkasına açıklayamaz ve işleme amacı dışında kullanamazlar. Bu yükümlülük görevden ayrılmalarından sonra da devam eder. (5) İşlenen kişisel verilerin kanuni olmayan yollarla başkaları tarafından elde edilmesi hâlinde, veri sorumlusu bu durumu en kısa sürede ilgilisine ve Kurula bildirir. Kurul, gerekmesi hâlinde bu durumu, kendi internet sitesinde ya da uygun göreceği başka bir yöntemle ilan edebilir.
- Cevapta aranan: (en kısa sürede) VE (Kurul)
- [x] Doğrulandı
- Not: 

### e29 — Veri sorumlusunun cevabından sonra Kurula şikâyet süresi ne kadardır?
- Beklenen kaynak: `kvkk:14` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6698&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > (1) Başvurunun reddedilmesi, verilen cevabın yetersiz bulunması veya süresinde başvuruya cevap verilmemesi hâllerinde; ilgili kişi, veri sorumlusunun cevabını öğrendiği tarihten itibaren otuz ve her hâlde başvuru tarihinden itibaren altmış gün içinde Kurula şikâyette bulunabilir. (2) 13 üncü madde uyarınca başvuru yolu tüketilmeden şikâyet yoluna başvurulamaz. (3) Kişilik hakları ihlal edilenlerin, genel hükümlere göre tazminat hakkı saklıdır.
- Cevapta aranan: (otuz | 30) VE (altmış | 60)
- [x] Doğrulandı
- Not: 

### e30 — Kurul şikâyete süresinde cevap vermezse ne olur?
- Beklenen kaynak: `kvkk:15` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6698&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … on beş gün içinde göndermek ve gerektiğinde yerinde inceleme yapılmasına imkân sağlamak zorundadır. (4) Şikâyet üzerine Kurul, talebi inceleyerek ilgililere bir cevap verir. Şikâyet tarihinden itibaren altmış gün içinde cevap verilmezse talep reddedilmiş sayılır. (5) Şikâyet üzerine veya resen yapılan inceleme sonucunda, ihlalin varlığının anlaşılması hâlinde Kurul, tespit ettiği hukuka aykırılıkların veri sorumlusu tarafından giderilmesine karar vererek ilgililere tebliğ eder. Bu karar, tebliğden itibaren …
- Cevapta aranan: (reddedilmiş)
- [x] Doğrulandı
- Not: 

### e31 — Veri Sorumluları Siciline ne zaman kaydolunmalıdır?
- Beklenen kaynak: `kvkk:16` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6698&MevzuatTur=1&MevzuatTertip=5)), `sicil-yon:5` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=24276&MevzuatTur=7&MevzuatTertip=5)), `sicil-yon:8` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=24276&MevzuatTur=7&MevzuatTertip=5))
- Kanıt (derlemden): > (1) Kurulun gözetiminde, Başkanlık tarafından kamuya açık olarak Veri Sorumluları Sicili tutulur. (2) Kişisel verileri işleyen gerçek ve tüzel kişiler, veri işlemeye başlamadan önce Veri Sorumluları Siciline kaydolmak zorundadır. Ancak, işlenen kişisel verinin niteliği, sayısı, veri işlemenin kanundan kaynaklanması veya üçüncü kişilere aktarılma durumu gibi Kurulca belirlenecek objektif kriterler göz önüne alınmak suretiyle, …
- Cevapta aranan: (başlamadan önce)
- [x] Doğrulandı
- Not: 

### e32 — Standart sözleşme imzalandıktan sonra Kuruma kaç gün içinde bildirilmelidir?
- Beklenen kaynak: `kvkk:9` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6698&MevzuatTur=1&MevzuatTertip=5)), `yurtdisi-aktarim-yon:14` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=40863&MevzuatTur=7&MevzuatTertip=5))
- Kanıt (derlemden): > … ek önlemler gibi hususları ihtiva eden standart sözleşmenin varlığı. ç) Yeterli korumayı sağlayacak hükümlerin yer aldığı yazılı bir taahhütnamenin varlığı ve Kurul tarafından aktarıma izin verilmesi. (5) Standart sözleşme, imzalanmasından itibaren beş iş günü içinde veri sorumlusu veya veri işleyen tarafından Kuruma bildirilir. (6) Veri sorumluları ve veri işleyenler, yeterlilik kararının bulunmaması ve dördüncü fıkrada öngörülen uygun güvencelerden herhangi birinin sağlanamaması durumunda, arızi olmak …
- Cevapta aranan: (beş iş günü | 5 iş günü)
- [x] Doğrulandı
- Not: 

### e33 — İlgili kişi verilerinin silinmesini talep ederse veri sorumlusu kaç gün içinde sonuçlandırmalıdır?
- Beklenen kaynak: `imha-yon:12` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=24038&MevzuatTur=7&MevzuatTertip=5)), `kvkk:13` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6698&MevzuatTur=1&MevzuatTertip=5)), `basvuru-teblig:6` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=24455&MevzuatTur=9&MevzuatTertip=5))
- Kanıt (derlemden): > … silinmesini veya yok edilmesini talep ettiğinde; a) Kişisel verileri işleme şartlarının tamamı ortadan kalkmışsa; veri sorumlusu talebe konu kişisel verileri siler, yok eder veya anonim hale getirir. Veri sorumlusu, ilgili kişinin talebini en geç otuz gün içinde sonuçlandırır ve ilgili kişiye bilgi verir. b) Kişisel verileri işleme şartlarının tamamı ortadan kalkmış ve talebe konu olan kişisel veriler üçüncü kişilere aktarılmışsa veri sorumlusu bu durumu üçüncü kişiye bildirir; üçüncü kişi nezdinde bu …
- Cevapta aranan: (otuz | 30)
- [x] Doğrulandı
- Not: 

### e34 — Saklama ve imha politikası hazırlama yükümlülüğü olmayan veri sorumlusu verileri ne kadar sürede silmelidir?
- Beklenen kaynak: `imha-yon:11` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=24038&MevzuatTur=7&MevzuatTertip=5))
- Kanıt (derlemden): > … belirlenir. Bu süre her halde altı ayı geçemez. (3) Kişisel veri saklama ve imha politikası hazırlama yükümlülüğü olmayan veri sorumlusu, kişisel verileri silme, yok etme veya anonim hale getirme yükümlülüğünün ortaya çıktığı tarihi takip eden üç ay içinde, kişisel verileri siler, yok eder veya anonim hale getirir. (4) Kurul, telafisi güç veya imkansız zararların doğması ve açıkça hukuka aykırılık olması halinde, bu maddede belirlenen süreleri kısaltabilir.
- Cevapta aranan: (üç ay | 3 ay)
- [x] Doğrulandı
- Not: 

### e35 — Silme ve yok etme işlemlerine ilişkin kayıtlar en az kaç yıl saklanır?
- Beklenen kaynak: `imha-yon:7` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=24038&MevzuatTur=7&MevzuatTertip=5))
- Kanıt (derlemden): > … imha politikasına uygun hareket edilmesi zorunludur. (3) Kişisel verilerin silinmesi, yok edilmesi ve anonim hale getirilmesiyle ilgili yapılan bütün işlemler kayıt altına alınır ve söz konusu kayıtlar, diğer hukuki yükümlülükler hariç olmak üzere en az üç yıl süreyle saklanır. (4) (Değişik:RG-28/4/2019-30758) Veri sorumlusu, kişisel verilerin silinmesi, yok edilmesi veya anonim hale getirilmesi işlemiyle ilgili uyguladığı yöntemleri ilgili politika ve prosedürlerinde açıklamakla yükümlüdür. (5) Veri …
- Cevapta aranan: (üç yıl | 3 yıl)
- [x] Doğrulandı
- Not: 

### e36 — Veri sorumlusu başvuruya yazılı cevap verirken kaç sayfaya kadar ücret alamaz?
- Beklenen kaynak: `basvuru-teblig:7` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=24455&MevzuatTur=9&MevzuatTertip=5))
- Kanıt (derlemden): > (1) İlgili kişinin başvurusuna yazılı olarak cevap verilecekse, on sayfaya kadar ücret alınmaz. On sayfanın üzerindeki her sayfa için 1 Türk Lirası işlem ücreti alınabilir. (2) Başvuruya cevabın CD, flash bellek gibi bir kayıt ortamında verilmesi halinde veri sorumlusu tarafından talep edilebilecek ücret kayıt ortamının …
- Cevapta aranan: (on sayfa | 10 sayfa)
- [x] Doğrulandı
- Not: 

### e37 — Açık rızaya dayanan işlemede aydınlatma ile açık rıza birlikte alınabilir mi?
- Beklenen kaynak: `aydinlatma-teblig:5` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=24454&MevzuatTur=9&MevzuatTertip=5))
- Kanıt (derlemden): > … e) Aydınlatma yükümlülüğünün yerine getirildiğinin ispatı veri sorumlusuna aittir. f) Kişisel veri işleme faaliyetinin açık rıza şartına dayalı olarak gerçekleştirilmesi halinde, aydınlatma yükümlülüğü ve açık rızanın alınması işlemlerinin ayrı ayrı yerine getirilmesi gerekmektedir. g) Aydınlatma yükümlülüğü kapsamında açıklanacak kişisel veri işleme amacının belirli, açık ve meşru olması gerekir. Aydınlatma yükümlülüğü yerine getirilirken, genel nitelikte ve muğlak ifadelere yer …
- Cevapta aranan: (ayrı ayrı | ayrı)
- [x] Doğrulandı
- Not: 

### e38 — İşveren, işten çıkardığı çalışanı şirketin sosyal medya hesabından duyurursa Kurul ne karar vermiştir?
- Beklenen kaynak: `kvkk-karar-2022-386` ([resmî metin](https://www.kvkk.gov.tr/Icerik/5406))
- Kanıt (derlemden): > … Kanun kapsamındaki bir işleme şartına dayanıldığına dair Kuruma somut herhangi bir bilgi, belge sunulmadığı hususları ile veri sorumlusunun ekonomik durumu dikkate alınarak, Kanun’un 18’inci maddesinin (1) numaralı fıkrasının (b) bendi uyarınca 30.000 TL idari para cezası uygulanmasına, - İlgili sosyal medya paylaşımında yer verilen kişisel verilerin imha edilerek sonucundan Kurula bilgi verilmesi hususunda veri sorumlusunun talimatlandırılmasına karar verilmiştir.
- Cevapta aranan: (30.000 | 30 bin | otuz bin)
- [x] Doğrulandı
- Not: 

### e39 — İnternet sitesinde reklam çerezlerinin açık rıza alınmadan kullanılması hakkında Kurul hangi yaptırımı uygulamıştır?
- Beklenen kaynak: `kvkk-karar-2022-1358` ([resmî metin](https://www.kvkk.gov.tr/Icerik/5406))
- Kanıt (derlemden): > … veri işlendiği, bu durumun ise Kanun’un 12’nci maddesinin (1) numaralı fıkrasında yer alan yükümlülüklere aykırılık teşkil ettiği dikkate alındığında veri sorumlusu hakkında Kanun’un 18’inci maddesinin (1) numaralı fıkrasının (b) bendi uyarınca 300.000 TL idari para cezası uygulanmasına, - Sitede çerezlerle işlenen kişisel veriler bakımından Kanun’un 10’uncu maddesi ile Aydınlatma Yükümlülüğünün Yerine Getirilmesinde Uyulacak Usul ve Esaslar Hakkında Tebliğ’in ilgili hükümlerine uygun biçimde ilgili kişilere yönelik …
- Cevapta aranan: (300.000 | 300 bin | üç yüz bin)
- [x] Doğrulandı
- Not: 

### e40 — Bir çalışanın izin bilgisinin birimdeki diğer personelle paylaşılması hakkında Kurul ne karar vermiştir?
- Beklenen kaynak: `kvkk-karar-2023-646` ([resmî metin](https://www.kvkk.gov.tr/Icerik/5406))
- Kanıt (derlemden): > … dayanmadığı ve bu durumun Kanun’un 12’nci maddesinin (1) numaralı fıkrasına aykırılık teşkil ettiği kanaatine varıldığından Kanun’un 18’inci maddesinin (3) numaralı fıkrası uyarınca veri sorumlusu bünyesinde görev yapan ilgili personel hakkında disiplin hükümlerine göre işlem yapılması ve işlemin sonucu hakkında Kurula bilgi verilmesi hususunda veri sorumlusunun talimatlandırılmasına karar verilmiştir.
- Cevapta aranan: (disiplin)
- [x] Doğrulandı
- Not: 

### e41 — Üniversitenin ders yoklamasını parmak iziyle alması Kurulca hukuka uygun bulunmuş mudur?
- Beklenen kaynak: `kvkk-karar-2024-197` ([resmî metin](https://www.kvkk.gov.tr/Icerik/5406))
- Kanıt (derlemden): > … uygun olacağı değerlendirmelerinden hareketle; - Veri sorumlusu bünyesinde ders yoklaması amacıyla biyometrik veri olan parmak izinin işlenmesinin Kanun’un özel nitelikli kişisel verilerin işlenmesine ilişkin 6 ncı maddesi kapsamında geçerli bir işleme şartına dayanmadığı, öte yandan veri işlemenin Kanunun 4 üncü maddesinde yer alan genel ilkelere de uygun olması gerektiği, biyometrik veri işlenmesi hususunda ilgili kişinin açık rızası bulunsa dahi bu durumun, Kanunun 4 üncü maddesinin ikinci fıkrasının (ç) …
- Cevapta aranan: (dayanmadığı | dayanma | ölçülü | hukuka aykırı | uygun bulunma)
- [x] Doğrulandı
- Not: 

### e42 — İşyerindeki kameraların konumu hakkında Kurul işverene ne talimat vermiştir?
- Beklenen kaynak: `kvkk-karar-2022-797` ([resmî metin](https://www.kvkk.gov.tr/Icerik/5406))
- Kanıt (derlemden): > … bir şekilde açıkça belirtildiği görülse de hangi kişisel verinin hangi işleme amacı ve hangi işleme şartı ile ilişkilendirildiğinin açıkça belirtilmediği, değerlendirmelerinden hareketle; - Veri sorumlusunun iş yerinde yer alan kameraları işçilerin makul mahremiyet beklentisini zedeleyecek bir şekilde konumlandırmaması, bu çerçevede iş yerlerindeki tüm kameraların gözden geçirilerek konumlarının düzenlenmesi, bu işlemlere ilişkin Kanun’un 15’inci maddesinin (5) numaralı fıkrası uyarınca Kurula en geç otuz gün içinde bilgi …
- Cevapta aranan: (mahremiyet)
- [x] Doğrulandı
- Not: 

### e43 — Banka çalışanı kendi telefon görüşmesi kayıtlarını isterse, Kurul kararına göre banka bunları nasıl vermelidir?
- Beklenen kaynak: `kvkk-karar-2024-592` ([resmî metin](https://www.kvkk.gov.tr/Icerik/5406))
- Kanıt (derlemden): > … konusu kayıtlara erişmesinde menfaatinin bulunduğu dikkate alındığında Kanun’un 11. maddesi kapsamında veri sorumlusunun ilgili kişinin talep ettiği telefon görüşme kayıtlarını üçüncü kişinin müşteri sırrı niteliğindeki bankacılık işlem verilerini maskeleyerek yazılı döküm yahut dijital ortamda aktarım suretiyle ilgili kişiye sağlaması ve sonucundan Kurula bilgi verilmesi hususunda talimatlandırılmasının uygun olacağı, Konuya ilişkin yürütülen inceleme neticesinde Kişisel Verileri Koruma Kurulunun …
- Cevapta aranan: (maskele)
- [x] Doğrulandı
- Not: 

### e44 — Havayolunun özel yolcu programı için açık rıza istemesi hakkında Kurul işlem yapmış mıdır?
- Beklenen kaynak: `kvkk-karar-2023-890` ([resmî metin](https://www.kvkk.gov.tr/Icerik/5406))
- Kanıt (derlemden): > … ve bu anlamda ilgili kişinin açık rızasının bir ürün veya hizmetin sunulmasının ya da ürün veya hizmetten yararlandırılmasının ön şartı olarak ileri sürülmesi niteliği taşımadığı dikkate alındığında veri sorumlusu hakkında Kanun kapsamında yapılacak bir işlem bulunmadığına karar verilmiştir.
- Cevapta aranan: (işlem bulunmadığı | işlem yapılma | işlem tesis edilme | ön şart)
- [x] Doğrulandı
- Not: 

### e45 — Doktorun hastanın ameliyat fotoğrafını kendi sosyal medyasında paylaşması üzerine Kurul ilgili kişiyi hangi konuda bilgilendirmiştir?
- Beklenen kaynak: `kvkk-karar-2022-630` ([resmî metin](https://www.kvkk.gov.tr/Icerik/5406))
- Kanıt (derlemden): > … yer alan belgelerden tevsik edilmiş olduğundan, veri sorumlusunun anılan iddialarına ilişkin olarak yargı yoluna başvurabileceği, - Öte yandan, Kanun’un 17’nci maddesinde kişisel verilere ilişkin suçlar bakımından 26/9/2004 tarih ve 5237 sayılı Türk Ceza Kanunu’nun 135 ila 140’ıncı madde hükümlerinin uygulanacağının düzenlendiği, Türk Ceza Kanunu’nun 135, 136 ve 137’nci maddelerinde hukuka aykırı olarak kişisel verileri kaydetme, kişisel verileri hukuka aykırı olarak verme, yayma veya ele geçirme suçuna …
- Cevapta aranan: (Türk Ceza Kanunu | TCK | yargı yolu)
- [x] Doğrulandı
- Not: 

### e46 — İş kazası Sosyal Güvenlik Kurumuna kaç gün içinde bildirilmelidir?
- Beklenen kaynak: `kvkk-karar-2022-797` ([resmî metin](https://www.kvkk.gov.tr/Icerik/5406)), `isg-kanunu:14` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6331&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … açan veya çalışan, işyeri ya da iş ekipmanını zarara uğratma potansiyeli olan olayları inceleyerek bunlar ile ilgili raporları düzenler. (2) İşveren, aşağıdaki hallerde belirtilen sürede Sosyal Güvenlik Kurumuna bildirimde bulunur: a) İş kazalarını kazadan sonraki üç iş günü içinde. b) Sağlık hizmeti sunucuları veya işyeri hekimi tarafından kendisine bildirilen meslek hastalıklarını, öğrendiği tarihten itibaren üç iş günü içinde. (3) İşyeri hekimi veya sağlık hizmeti sunucuları; meslek hastalığı ön tanısı koydukları …
- Cevapta aranan: (üç iş günü | 3 iş günü)
- [x] Doğrulandı
- Not: 

### e47 — İş sağlığı ve güvenliği kurulu en az kaç çalışanı olan işyerlerinde oluşturulur?
- Beklenen kaynak: `isg-kanunu:22` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6331&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > (1) Elli ve daha fazla çalışanın bulunduğu ve altı aydan fazla süren sürekli işlerin yapıldığı işyerlerinde işveren, iş sağlığı ve güvenliği ile ilgili çalışmalarda bulunmak üzere kurul oluşturur. İşveren, iş sağlığı ve güvenliği mevzuatına uygun kurul kararlarını uygular. (2) …
- Cevapta aranan: (elli | 50)
- [x] Doğrulandı
- Not: 

### e48 — İşveren, işin durdurulması kararına kaç gün içinde ve nereye itiraz edebilir?
- Beklenen kaynak: `isg-kanunu:25` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6331&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … getirilir. Ancak, tespit edilen hususun acil müdahaleyi gerektirmesi nedeniyle verilen işin durdurulması kararı, mülki idare amiri tarafından kolluk kuvvetleri marifetiyle aynı gün yerine getirilir. (4) İşveren, yerine getirildiği tarihten itibaren altı iş günü içinde, yetkili iş mahkemesinde işin durdurulması kararına itiraz edebilir. İtiraz, işin durdurulması kararının uygulanmasını etkilemez. Mahkeme itirazı öncelikle görüşür ve altı iş günü içinde karara bağlar. Mahkeme kararı kesindir. (5) İşverenin işin durdurulmasını gerektiren …
- Cevapta aranan: (altı iş günü | 6 iş günü) VE (iş mahkemesi)
- [x] Doğrulandı
- Not: 

### e49 — Ciddi ve yakın tehlike nedeniyle çalışmaktan kaçınan çalışanın o dönemdeki ücreti ne olur?
- Beklenen kaynak: `isg-kanunu:13` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6331&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … tutanakla tespit eder. Karar, çalışana ve çalışan temsilcisine yazılı olarak bildirilir. (2) Kurul veya işverenin çalışanın talebi yönünde karar vermesi hâlinde çalışan, gerekli tedbirler alınıncaya kadar çalışmaktan kaçınabilir. Çalışanların çalışmaktan kaçındığı dönemdeki ücreti ile kanunlardan ve iş sözleşmesinden doğan diğer hakları saklıdır. (3) Çalışanlar ciddi ve yakın tehlikenin önlenemez olduğu durumlarda birinci fıkradaki usule uymak zorunda olmaksızın işyerini veya tehlikeli bölgeyi terk ederek belirlenen güvenli …
- Cevapta aranan: (saklı)
- [x] Doğrulandı
- Not: 

### e50 — Altı aydan fazla işten uzak kalan çalışana tekrar işe başlamadan önce hangi eğitim verilir?
- Beklenen kaynak: `isg-kanunu:17` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6331&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … (4) İş kazası geçiren veya meslek hastalığına yakalanan çalışana işe başlamadan önce, söz konusu kazanın veya meslek hastalığının sebepleri, korunma yolları ve güvenli çalışma yöntemleri ile ilgili ilave eğitim verilir. Ayrıca, herhangi bir sebeple altı aydan fazla süreyle işten uzak kalanlara, tekrar işe başlatılmadan önce bilgi yenileme eğitimi verilir. (5) Tehlikeli ve çok tehlikeli sınıfta yer alan işyerlerinde; yapılacak işlerde karşılaşılacak sağlık ve güvenlik riskleri ile ilgili yeterli bilgi ve talimatları içeren …
- Cevapta aranan: (bilgi yenileme)
- [x] Doğrulandı
- Not: 

### d01 — 2026 yılında kıdem tazminatı tavanı kaç liradır?
- Beklenen: **kapsam dışı** (sistem "bilmiyorum" demeli)
- [x] Doğrulandı
- Not: 

### d03 — İş mahkemesinde dava açmadan önce arabuluculuk görüşmeleri en fazla kaç hafta sürer?
- Beklenen: **kapsam dışı** (sistem "bilmiyorum" demeli)
- **Claude notu (14 Kas):** Geniş katman eklenince bu soru derlemde cevaplanabilir hale geldi; sistem 7036 s. İş Mahkemeleri Kanunu m. 3'ten doğru ve atıflı cevap veriyor. Öneri: etiketi 'kapsam içi (geniş katman)' yap, beklenen kaynak `kanun-7036:3`. Karar senin.
- [x] Doğrulandı
- Not: 

### d04 — GDPR'a göre veri ihlali denetim otoritesine kaç saat içinde bildirilir?
- Beklenen: **kapsam dışı** (sistem "bilmiyorum" demeli)
- [x] Doğrulandı
- Not: 

### d05 — Anonim şirket en az kaç ortakla kurulabilir?
- Beklenen: **kapsam dışı** (sistem "bilmiyorum" demeli)
- **Claude notu (14 Kas):** Geniş katman eklenince bu soru derlemde cevaplanabilir hale geldi; sistem 6102 s. TTK m. 338'ten doğru ve atıflı cevap veriyor. Öneri: etiketi 'kapsam içi (geniş katman)' yap, beklenen kaynak `kanun-6102:338`. Karar senin.
- [x] Doğrulandı
- Not: 

### d06 — Konut satışında tapu harcı oranı yüzde kaçtır?
- Beklenen: **kapsam dışı** (sistem "bilmiyorum" demeli)
- [x] Doğrulandı
- Not: 

### d07 — Trafik cezasına itiraz süresi kaç gündür?
- Beklenen: **kapsam dışı** (sistem "bilmiyorum" demeli)
- [x] Doğrulandı
- Not: 

## Geniş katman seti (18 soru, taslak)

### g01 — Konut kira artışlarında yenilenen kira döneminde yasal üst sınır nasıl belirlenir?
- Beklenen kaynak: `kanun-6098:344` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6098&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > Tarafların yenilenen kira dönemlerinde uygulanacak kira bedeline ilişkin anlaşmaları, bir önceki kira yılında tüketici fiyat endeksindeki oniki aylık ortalamalara göre değişim oranını geçmemek koşuluyla geçerlidir. Bu kural, bir yıldan daha uzun süreli kira sözleşmelerinde de uygulanır. Taraflarca bu konuda bir anlaşma yapılmamışsa, kira bedeli, bir önceki kira yılının tüketici fiyat …
- Cevapta aranan: (tüketici fiyat endeks | oniki aylık | ortalama)
- [x] Doğrulandı
- Not: 

### g02 — Anlaşmalı boşanma davası açabilmek için evliliğin en az ne kadar sürmüş olması gerekir?
- Beklenen kaynak: `kanun-4721:166` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4721&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … ise, davalının açılan davaya itiraz hakkı vardır. Bununla beraber bu itiraz, hakkın kötüye kullanılması niteliğinde ise ve evlilik birliğinin devamında davalı ve çocuklar bakımından korunmaya değer bir yarar kalmamışsa boşanmaya karar verilebilir. Evlilik en az bir yıl sürmüş ise, eşlerin birlikte başvurması ya da bir eşin diğerinin davasını kabul etmesi hâlinde, evlilik birliği temelinden sarsılmış sayılır. Bu hâlde boşanma kararı verilebilmesi için, hâkimin tarafları bizzat dinleyerek iradelerinin serbestçe açıklandığına …
- Cevapta aranan: (en az bir yıl) VE (temelinden sarsılmış)
- [x] Doğrulandı
- Not: 

### g03 — Tacirler arasında temerrüde düşürme veya sözleşmeden dönme ihtarları hangi yollarla yapılabilir?
- Beklenen kaynak: `kanun-6102:18` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6102&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … da yükümlüdür. (2) Her tacirin, ticaretine ait bütün faaliyetlerinde basiretli bir iş adamı gibi hareket etmesi gerekir. (3) Tacirler arasında, diğer tarafı temerrüde düşürmeye, sözleşmeyi feshe, sözleşmeden dönmeye ilişkin ihbarlar veya ihtarlar noter aracılığıyla, taahhütlü mektupla, telgrafla veya güvenli elektronik imza kullanılarak kayıtlı elektronik posta sistemi ile yapılır. (4) Tacir sıfatına bağlı olan diğer hükümler saklıdır. II - Özel olarak 1.
- Cevapta aranan: (noter) VE (taahhütlü mektup | telgraf) VE (kayıtlı elektronik posta | güvenli elektronik imza)
- [x] Doğrulandı
- Not: 

### g04 — Mal teslim edildikten veya hizmet yapıldıktan sonra fatura en geç kaç gün içinde düzenlenmelidir?
- Beklenen kaynak: `kanun-213:231` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=213&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … takdirde her birine kaçıncı örnek olduğu işaret edilir. 4. Faturaların baş tarafında iş sahibinin veya namına imzaya mezun olanların imzası bulunur. 5. (Değişik: 4/12/1985-3239/20 md.) Fatura, malın teslimi veya hizmetin yapıldığı tarihten itibaren azami yedi gün içinde düzenlenir. (Ek cümle:29/4/2021-7318/1 md.) Hazine ve Maliye Bakanlığı; mal veya hizmetin nev’i, miktarı, fiyatı, tutarı, satışın yapılma şekli, faaliyet konusu, sektör veya mükellefiyet türünü ayrı ayrı veya birlikte dikkate alarak, bu süreyi indirmeye ya da …
- Cevapta aranan: (yedi gün | 7 gün)
- [x] Doğrulandı
- Not: 

### g05 — Hukuk mahkemesinin kararına karşı istinaf yoluna başvuru süresi kaç haftadır ve ne zaman işlemeye başlar?
- Beklenen kaynak: `kanun-6100:345` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6100&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > (1) İstinaf yoluna başvuru süresi iki haftadır. Bu süre, ilamın usulen taraflardan her birine tebliğiyle işlemeye başlar. İstinaf yoluna başvuru süresine ilişkin özel kanun hükümleri saklıdır.
- Cevapta aranan: (iki hafta) VE (tebliği)
- [x] Doğrulandı
- Not: 

### g06 — İlamsız icra takibinde ödeme emrini alan borçlu kaç gün içinde ve nereye itiraz etmelidir?
- Beklenen kaynak: `kanun-2004:62` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=2004&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > (Değişik: 18/2/1965-538/33 md.) İtiraz etmek istiyen borçlu, itirazını, ödeme emrinin tebliği tarihinden itibaren yedi gün içinde dilekçe ile veya sözlü olarak icra dairesine bildirmeye mecburdur. (Değişik ikinci cümle: 17/7/2003-4949/13 md.) İtiraz, takibi yapan icra dairesinden başka bir icra dairesine yapıldığı takdirde bu daire gereken masrafı itirazla birlikte …
- Cevapta aranan: (yedi gün | 7 gün) VE (icra dairesine)
- [x] Doğrulandı
- Not: 

### g07 — İnternetten yapılan mesafeli satışlarda tüketici gerekçe göstermeden kaç gün içinde sözleşmeden cayabilir?
- Beklenen kaynak: `kanun-6502:48` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6502&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … doğrultusunda hazırlanan mallara ilişkin sözleşmeler haricinde mal satışlarında bu süre her hâlükârda otuz günü geçemez. Satıcı veya sağlayıcının bu süre içinde edimini yerine getirmemesi durumunda tüketici sözleşmeyi feshedebilir. (4) Tüketici, on dört gün içinde herhangi bir gerekçe göstermeksizin ve cezai şart ödemeksizin sözleşmeden cayma hakkına sahiptir. Cayma hakkının kullanıldığına dair bildirimin bu süre içinde satıcı veya sağlayıcıya yöneltilmiş olması yeterlidir. Satıcı veya sağlayıcı, cayma hakkı konusunda …
- Cevapta aranan: (on dört gün | 14 gün) VE (cezai şart)
- [x] Doğrulandı
- Not: 

### g08 — Basit hırsızlık suçunun kanunda öngörülen hapis cezası alt ve üst sınırı nedir?
- Beklenen kaynak: `kanun-5237:141` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=5237&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > (1) Zilyedinin rızası olmadan başkasına ait taşınır bir malı, kendisine veya başkasına bir yarar sağlamak maksadıyla bulunduğu yerden alan kimseye bir yıldan üç yıla kadar hapis cezası verilir.
- Cevapta aranan: (bir yıldan üç yıla | 1 yıldan 3 yıla)
- [x] Doğrulandı
- Not: 

### g09 — Trafik kontrolünde alkol ölçümü için teknik cihaza üflemeye izin vermeyen sürücü hakkında ne işlem yapılır?
- Beklenen kaynak: `kanun-2918:48` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=2918&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … kullanılır. Kişinin yaralanmalı veya ölümlü ya da kollukça müdahil olunan maddi hasarlı trafik kazasına karışması hâlinde, ikinci fıkrada belirtilen muayeneye tabi tutulması zorunludur. Teknik cihaz ile yapılan ölçüme itiraz eden veya bu cihaz ile ölçüm yapılmasına müsaade etmeyen bu sürücüler, en yakın adli tıp kurumuna veya adli tabipliğe veya Sağlık Bakanlığına bağlı sağlık kuruluşlarına götürülerek uyuşturucu veya uyarıcı madde ya da alkol tespitinde kullanılmak üzere vücutlarından kan, tükürük veya idrar gibi örnekler …
- Cevapta aranan: (adli tıp | sağlık kuruluş) VE (kan | tükürük | idrar)
- [x] Doğrulandı
- Not: 

### g10 — İşveren yeni işe alacağı işçinin sigortalı işe giriş bildirgesini SGK'ya ne zaman vermek zorundadır?
- Beklenen kaynak: `kanun-5510:8` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=5510&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > (Değişik birinci fıkra: 17/4/2008-5754/6 md.) İşverenler, 4 üncü maddenin birinci fıkrasının (a) bendi kapsamında sigortalı sayılan kişileri, 7 nci maddenin birinci fıkrasının (a) bendinde belirtilen sigortalılık başlangıç tarihinden önce, sigortalı işe giriş bildirgesi ile Kuruma bildirmekle yükümlüdür. Ancak işveren tarafından sigortalı işe giriş bildirgesi; a) İnşaat, balıkçılık ve tarım işyerlerinde işe başlatılacak sigortalılar için, en geç çalışmaya başlatıldığı gün, b) …
- Cevapta aranan: (başlangıç tarihinden önce) VE (çalışmaya başlatıldığı gün)
- [x] Doğrulandı
- Not: 

### g11 — Kamu ihalesi sürecinde hukuka aykırılık iddiasıyla ihaleyi yapan idareye şikayet başvurusu kaç gün içinde yapılır?
- Beklenen kaynak: `kanun-4734:55` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=4734&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … md.) Şikayet başvurusu, ihale sürecindeki işlem veya eylemlerin hukuka aykırılığı iddiasıyla bu işlem veya eylemlerin farkına varıldığı veya farkına varılmış olması gereken tarihi izleyen günden itibaren 21 inci maddenin (b) ve (c) bentlerine göre yapılan ihalelerde beş gün, diğer hallerde ise on gün içinde ve sözleşmenin imzalanmasından önce, ihaleyi yapan idareye yapılır. İlanda yer alan hususlara yönelik başvuruların süresi ilk ilan tarihinden, ön yeterlik veya ihale dokümanının ilana yansımayan diğer hükümlerine yönelik başvuruların süresi …
- Cevapta aranan: (beş gün | 5 gün) VE (on gün | 10 gün)
- [x] Doğrulandı
- Not: 

### g12 — Bireysel işlenen suçlarda gözaltı süresi en fazla ne kadar sürebilir?
- Beklenen kaynak: `kanun-5271:91` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=5271&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > … Savcılığınca bırakılmazsa, soruşturmanın tamamlanması için gözaltına alınmasına karar verilebilir. (Değişik ikinci cümle: 25/5/2005 – 5353/8 md.) Gözaltı süresi, yakalama yerine en yakın hâkim veya mahkemeye gönderilmesi için zorunlu süre hariç, yakalama anından itibaren yirmidört saati geçemez. (Ek cümle: 25/5/2005 – 5353/8 md.) Yakalama yerine en yakın hâkim veya mahkemeye gönderilme için zorunlu süre oniki saatten fazla olamaz. (2) Gözaltına alma, bu tedbirin soruşturma yönünden zorunlu olmasına ve kişinin bir suçu işlediği şüphesini …
- Cevapta aranan: (yirmidört saat | 24 saat) VE (oniki saat | 12 saat)
- [x] Doğrulandı
- Not: 

### g13 — Kadın devlet memuruna doğumdan önce ve sonra toplam kaç hafta analık izni verilir?
- Beklenen kaynak: `kanun-657:104` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=657&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > (Değişik: 13/2/2011 - 6111/106 md.) A) Kadın memura; doğumdan önce sekiz, doğumdan sonra sekiz hafta olmak üzere toplam onaltı hafta süreyle analık izni verilir. Çoğul gebelik durumunda, doğum öncesi sekiz haftalık analık izni süresine iki hafta eklenir. Ancak beklenen doğum tarihinden sekiz hafta öncesine kadar sağlık durumunun çalışmaya uygun olduğunu tabip raporuyla belgeleyen kadın memur, …
- Cevapta aranan: (sekiz hafta | sekiz,) VE (onaltı hafta | 16 hafta)
- [x] Doğrulandı
- Not: 

### g14 — Bir takvim yılına ait yıllık gelir vergisi beyannamesi ne zamana kadar vergi dairesine verilir?
- Beklenen kaynak: `kanun-193:92` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=193&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > (Değişik: 19/2/1963-202/46 md.) (Değişik birinci fıkra: 9/4/2003-4842/11 md.) Bir takvim yılına ait beyanname izleyen yılın Mart ayının başından yirmibeşinci günü akşamına kadar (…) [102] tam mükellefiyette vergiyi tarha yetkili vergi dairesine, dar mükellefiyette Türkiye'de vergi muhatabı mevcutsa onun Türkiye'de oturduğu yerin, Türkiye'de vergi muhatabı yoksa işyerinin, işyeri birden fazla ise bu …
- Cevapta aranan: (Mart ayının) VE (yirmibeşinci günü | 25)
- [x] Doğrulandı
- Not: 

### g15 — Özel kanunda ayrı süre öngörülmemişse idare mahkemesi ve vergi mahkemesinde dava açma süresi kaç gündür?
- Beklenen kaynak: `kanun-2577:7` ([resmî metin](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=2577&MevzuatTur=1&MevzuatTertip=5))
- Kanıt (derlemden): > 1. Dava açma süresi, özel kanunlarında ayrı süre gösterilmeyen hallerde Danıştayda ve idare mahkemelerinde altmış ve vergi mahkemelerinde otuz gündür. 2. Bu süreler; a) İdari uyuşmazlıklarda; yazılı bildirimin yapıldığı, b) Vergi, resim ve harçlar ile benzeri mali yükümler ve bunların zam ve cezalarından doğan uyuşmazlıklarda: Tahakkuku tahsile bağlı olan vergilerde tahsilatın; tebliğ …
- Cevapta aranan: (altmış | 60) VE (otuz | 30)
- [x] Doğrulandı
- Not: 

### g16 — 2026 yılı için geçerli net asgari ücret tutarı kaç TL olarak belirlenmiştir?
- Beklenen: **kapsam dışı** (sistem "bilmiyorum" demeli)
- [x] Doğrulandı
- Not: 

### g17 — Türkiye'de 10 yıl kıdemli bir yazılım mühendisinin ortalama piyasa maaşı nedir?
- Beklenen: **kapsam dışı** (sistem "bilmiyorum" demeli)
- [x] Doğrulandı
- Not: 

### g18 — Ankara'daki ehliyet direksiyon sınavı randevu takvimi hangi tarihte açıklanmaktadır?
- Beklenen: **kapsam dışı** (sistem "bilmiyorum" demeli)
- [x] Doğrulandı
- Not: 

