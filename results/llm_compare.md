# LLM karşılaştırması (5 soru, aynı bağlam)

Sorular eval setinden değil. Arama eşiği kapalı. İçerik doğruluğu elle okunmalı; tablo yalnızca otomatik ölçülenleri verir.

| Model | Ort. süre (sn) | Geçerli atıf | Geçersiz atıf | Atıfsız cevap | Kapsam dışında CEVAP_YOK | Hata |
|---|---|---|---|---|---|---|
| ollama:qwen2.5:7b | 5.8 | 7 | 0 | 0 | evet | 0 |
| ollama:qwen3:8b | 4.7 | 6 | 0 | 0 | evet | 0 |
| gemini | 14.7 | 6 | 0 | 1 | HAYIR | 2 |

## Cevaplar

### ollama:qwen2.5:7b — c01: İşçi iş sözleşmesini feshederken ne kadar önceden haber vermeli?

_10.6 sn | atıflar: 4857 s. İş Kanunu m. 17 | geçersiz: []_

> İşçi iş sözleşmesini feshederken önceden belirli sürelerde haber vermeli:
> 
> - İşi altı aydan az sürmüş olan işçi için, bildirimin diğer tarafa yapılmasından başlayarak iki hafta sonra feshedilir. [1][1]
> - İşi altı aydan bir buçuk yıla kadar sürmüş olan işçi için, bildirimin diğer tarafa yapılmasından başlayarak dört hafta sonra feshedilir. [1][1]
> - İşi bir buçuk yıldan üç yıla kadar sürmüş olan işçi için, bildirimin diğer tarafa yapılmasından başlayarak altı hafta sonra feshedilir. [1][1]
> - İşi üç yıldan fazla sürmüş işçi için, bildirim yapılmasından başlayarak sekiz hafta sonra feshedilir. [1][1]
> 
> Bu süreler asgari olup sözleşmeler ile artırılabilir. [1][1]

### ollama:qwen2.5:7b — c02: Gece çalışması en fazla kaç saat sürebilir?

_3.1 sn | atıflar: 4857 s. İş Kanunu m. 69; Fazla Çalışma Yön. m. 7 | geçersiz: []_

> Gece çalışması en fazla yedibusuk saati sürebilir. Ancak, turizm, özel güvenlik, sağlık hizmeti ve 30/5/2013 tarihli ve 6491 sayılı Türk Petrol Kanunu uyarınca petrol araştırma, arama ve sondaj faaliyetleri kapsamında yürütülen işlerde işçinin yazılı onayının alınması şartıyla yedi buçuk saatin üzerinde gece çalışması yaptırılabilir. [1][3]

### ollama:qwen2.5:7b — k01: İşveren işyerindeki güvenlik kamerasıyla ses kaydı alabilir mi?

_8.2 sn | atıflar: KVKK Kurulu K. 2023/2007 (Kurulun değerlendirmesi/1); KVKK Kurulu K. 2023/2007 (karar (hüküm)) | geçersiz: []_

> EVET, işveren işyerindeki güvenlik kameraları vasıtasıyla ses kaydı alabilir, ancak bu alınışta bazı koşulların karşılanması gerekmektedir. [1][2]
> 
> İlk olarak, ses kaydı almanın güvenliği sağlama amacını gerçekleştirebileceği ve bu amaca ulaşmak için gerekli olan birtakım hususların değerlendirilmesi gerekmektedir. [1] Bu, işyerindeki fiziksel mekan güvenliğinin sağlanması ve çalışanlar ve ziyaretçiler arasında çıkabilecek kargaşaların önlenmesi gibi durumlar için geçerlidir. [1]
> 
> Ancak, ses kaydı almanın her zaman gerekli olmadığı belirtilmiştir. [1] Veri sorumlusu, güvenlik kameraları vasıtasıyla görüntü kaydı alması, güvenliği sağlama amacına uygun bir şekilde yerine getirilebileceği ve bu amaca ulaşmak için gerekli olan birtakım hususların değerlendirilmesi gereklidir. [1] Bu bağlamda, ses kaydı almanın gerekli olmadığı ve hukuka aykırı olarak gerçekleştirilmesi durumunda veri sorumlusu idari cezalara tabi kalabilir. [2]
> 
> Sonuç olarak, işyerindeki güvenlik kameraları vasıtasıyla ses kaydı almanın gerekli olup olmadığı, güvenliği sağlama amacına uygun bir şekilde değerlendirilmesi ve hukuka uygun bir şekilde gerçekleştirilmesi gibi faktörlere bağlıdır. [1][2]

### ollama:qwen2.5:7b — k03: Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyebilir mi?

_4.1 sn | atıflar: KVKK Kurulu K. 2023/426 (Kurulun değerlendirmesi/8); KVKK Kurulu K. 2023/426 (karar (hüküm)) | geçersiz: []_

> Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyemez, çünkü bu durum KVKK'nin 12. maddesine aykırıdır. KVKK Kurulu KVKK Kurulu K. 2023/426 kararı, finansman şirketinin e-Devlet şifrelerini talep etmesinin herhangi bir veri işleme şartına dayanmamakla birlikte Kanun'un 12. maddesinin (1) numaralı fıkrasına uygun olmamasından dolayı idari para cezasına yol açtığını belirtmiştir. [1][2]

### ollama:qwen2.5:7b — r10: 2026 yılında net asgari ücret ne kadardır?

_2.9 sn | atıflar: — | geçersiz: []_

> CEVAP_YOK
> 
> Net asgari ücret 2026 yılına kadar belirlenmemiş, çünkü Kanun 4857'nin 39 maddesine göre ücretler en geç iki yılda bir belirlenir. Son güncel asgari ücret belirleme tarihi 2018 yılına dayanıyor ve bu tarihten sonra herhangi bir güncelleme kaydedilmedi. [1]

### ollama:qwen3:8b — c01: İşçi iş sözleşmesini feshederken ne kadar önceden haber vermeli?

_8.4 sn | atıflar: 4857 s. İş Kanunu m. 17; 4857 s. İş Kanunu m. 24 | geçersiz: []_

> İşçi, iş sözleşmesini feshederken, haklı nedenle fesih hakkı kullanıyorsa, bu hakkı kullanmadan önce işverene bildirilmesi gerekir. Haklı nedenler kapsamında işverenin ahlak ve iyi niyet kurallarına uymadığı durumlarda, işçi bu durumu öğrendiği günden itibaren altı iş günü içinde fesih hakkını kullanabilir [3]. Ayrıca, işverenin bildirim süresine uymaması veya ücreti peşin ödememesi durumunda, işçi bu süreyi bildirim süresine ekleyerek kullanabilir [1].

### ollama:qwen3:8b — c02: Gece çalışması en fazla kaç saat sürebilir?

_3.5 sn | atıflar: 4857 s. İş Kanunu m. 69 | geçersiz: []_

> Gece çalışması en fazla yedibuçuk saat sürebilir. Ancak, turizm, özel güvenlik, sağlık hizmeti ve 30/5/2013 tarihli ve 6491 sayılı Türk Petrol Kanunu uyarınca petrol araştırma, arama ve sondaj faaliyetleri kapsamında yürütülen işlerde, işçinin yazılı onayının alınması şartıyla yedi buçuk saatin üzerinde gece çalışması yaptırılabilir [1].

### ollama:qwen3:8b — k01: İşveren işyerindeki güvenlik kamerasıyla ses kaydı alabilir mi?

_5.5 sn | atıflar: KVKK Kurulu K. 2023/2007 (Kurulun değerlendirmesi/1); KVKK Kurulu K. 2023/2007 (karar (hüküm)) | geçersiz: []_

> İşveren, işyerindeki güvenlik kamerasıyla ses kaydı alabilir; ancak bu işleme faaliyeti, Kanun’un 5’inci maddesinin 2’nci fıkrasının (f) bendi çerçevesinde veri sorumlusunun meşru menfaatleri için veri işlenmesinin zorunlu olması şartına uygun olmalıdır. Ses kaydı alınmasında meşru menfaatin bulunmadığı, zorunluluk arz etmediği ve kişisel veri işlenmeksizin başkaca bir yolun mümkün olmadığı tespit edilmiştir [1]. Bu nedenle, ses kaydı alınması hukuka aykırı olarak gerçekleştirilmiş olup, veri sorumlusu hakkında idari para cezası uygulanmıştır [2].

### ollama:qwen3:8b — k03: Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyebilir mi?

_4.3 sn | atıflar: KVKK Kurulu K. 2023/426 (karar (hüküm)) | geçersiz: []_

> Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyemez. KVKK Kurulunun 2023/426 sayılı kararı uyarınca, e-Devlet şifresi talep edilmesi, kişisel verilerin hukuka aykırı olarak işlenmesine yol açabilir. Bu tür bir işlem, Kanun’un 12’nci maddesinin (1) numaralı fıkrasında yer alan yükümlülüklerini yerine getirmemektedir [2].

### ollama:qwen3:8b — r10: 2026 yılında net asgari ücret ne kadardır?

_1.8 sn | atıflar: — | geçersiz: []_

> CEVAP_YOK  
> KAYNAKLARDA 2026 yılında net asgari ücretin miktarı belirtilmemiştir.

### gemini — c01: İşçi iş sözleşmesini feshederken ne kadar önceden haber vermeli?

_2.5 sn | atıflar: 4857 s. İş Kanunu m. 17; 4857 s. İş Kanunu m. 24 | geçersiz: []_

> Belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir [1]. İhbar süreleri işçinin kıdemine göre belirlenir ve şu şekildedir:
> 
> * İşi 6 aydan az sürmüş işçi için 2 hafta [1],
> * İşi 6 aydan 1,5 yıla kadar sürmüş işçi için 4 hafta [1],
> * İşi 1,5 yıldan 3 yıla kadar sürmüş işçi için 6 hafta [1],
> * İşi 3 yıldan fazla sürmüş işçi için 8 hafta [1].
> 
> Bu süreler asgari olup sözleşmeler ile artırılabilir [1]. Ancak işçi, Kanun'da sayılan sağlık sebepleri, ahlak ve iyiniyet kurallarına uymayan haller veya zorlayıcı sebeplerin varlığı halinde iş sözleşmesini bildirim süresini beklemeksizin derhal feshedebilir [3].

### gemini — c02: Gece çalışması en fazla kaç saat sürebilir?

_1.3 sn | atıflar: 4857 s. İş Kanunu m. 69 | geçersiz: []_

> İşçilerin gece çalışmaları kural olarak yedibuçuk saati geçemez [1]. Ancak turizm, özel güvenlik, sağlık hizmeti ve Türk Petrol Kanunu uyarınca petrol araştırma, arama ve sondaj faaliyetleri kapsamında yürütülen işlerde, işçinin yazılı onayının alınması şartıyla yedi buçuk saatin üzerinde gece çalışması yaptırılabilir [1].

### gemini — k01: İşveren işyerindeki güvenlik kamerasıyla ses kaydı alabilir mi?

_11.8 sn | atıflar: KVKK Kurulu K. 2023/2007 (Kurulun değerlendirmesi/1); KVKK Kurulu K. 2023/2007 (karar (hüküm)); KVKK Kurulu K. 2024/1361 (karar (hüküm)/2) | geçersiz: []_

> Kurulun bir değerlendirmesinde, güvenlik amacıyla kamerayla görüntü kaydı alınması yeterli görülmüş ve ayrıca ses kaydı alınmasında veri sorumlusunun meşru menfaatinin bulunmadığı tespit edilmiştir [1]. Somut bir olayda Kurul; güvenlik kulübesindeki kameralar vasıtasıyla ses verilerinin işlenmesinde hukuka uygun bir veri işleme sebebi bulunmadığına karar vermiş ve bu aykırılık nedeniyle veri sorumlusuna idari para cezası uygulayarak hukuka aykırı işlenen ses verilerinin imha edilmesini talimatlandırmıştır [1][2]. Ayrıca Kurul, güvenlik kamerasıyla ses kaydı alındığı iddiasının tevsik edilemediği başka bir somut olayda, sadece görüntü kaydı alınmasını veri sorumlusunun hukuki yükümlülüğü kapsamında hukuka uygun bulmuştur [5]. 
> 
> İşverenin genel olarak işyerinde güvenlik kamerasıyla ses kaydı alıp alamayacağına dair mevzuattaki genel kural metinde yer almamaktadır.

### gemini — k03: Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyebilir mi?

_29.8 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: Gemini 429: {
>   "error": {
>     "code": 429,
>     "message": "You exceeded your current quota, please check your plan and billing details. For more info

### gemini — r10: 2026 yılında net asgari ücret ne kadardır?

_28.3 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: Gemini 429: {
>   "error": {
>     "code": 429,
>     "message": "You exceeded your current quota, please check your plan and billing details. For more info

