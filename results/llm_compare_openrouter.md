# LLM karşılaştırması (5 soru, aynı bağlam)

Sorular eval setinden değil. Arama eşiği kapalı. İçerik doğruluğu elle okunmalı; tablo yalnızca otomatik ölçülenleri verir.

| Model | Ort. süre (sn) | Geçerli atıf | Geçersiz atıf | Atıfsız cevap | Kapsam dışında CEVAP_YOK | Hata |
|---|---|---|---|---|---|---|
| openrouter:google/gemma-4-31b-it:free | 3.5 | 0 | 0 | 4 | HAYIR | 5 |
| openrouter:nvidia/nemotron-3-ultra-550b-a55b:free | 4.3 | 6 | 0 | 0 | evet | 0 |
| openrouter:baidu/ernie-5.5-flash-preview:free | 0.1 | 0 | 0 | 4 | HAYIR | 5 |
| openrouter:inclusionai/ling-3.0-flash | 2.1 | 8 | 0 | 0 | evet | 0 |
| openrouter:mistralai/mistral-nemo | 11.0 | 5 | 0 | 1 | evet | 0 |
| openrouter:qwen/qwen3.7-flash | 4.7 | 9 | 0 | 0 | evet | 0 |
| openrouter:z-ai/glm-5.3-flash | 0.1 | 0 | 0 | 4 | HAYIR | 5 |
| openrouter:deepseek/deepseek-v4.1-flash-1017 | 2.2 | 9 | 0 | 0 | evet | 0 |
| openrouter:openai/gpt-5-nano | 0.1 | 0 | 0 | 4 | HAYIR | 5 |

## Cevaplar

### openrouter:google/gemma-4-31b-it:free — c01: İşçi iş sözleşmesini feshederken ne kadar önceden haber vermeli?

_3.6 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 429: Provider returned error

### openrouter:google/gemma-4-31b-it:free — c02: Gece çalışması en fazla kaç saat sürebilir?

_3.4 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 429: Provider returned error

### openrouter:google/gemma-4-31b-it:free — k01: İşveren işyerindeki güvenlik kamerasıyla ses kaydı alabilir mi?

_3.5 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 429: Provider returned error

### openrouter:google/gemma-4-31b-it:free — k03: Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyebilir mi?

_3.5 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 429: Provider returned error

### openrouter:google/gemma-4-31b-it:free — r10: 2026 yılında net asgari ücret ne kadardır?

_3.4 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 429: Provider returned error

### openrouter:nvidia/nemotron-3-ultra-550b-a55b:free — c01: İşçi iş sözleşmesini feshederken ne kadar önceden haber vermeli?

_2.7 sn | atıflar: 4857 s. İş Kanunu m. 17 | geçersiz: []_

> Belirsiz süreli iş sözleşmelerinde işçinin fesih bildirimi yapmasından sonra işin ne zaman feshedilmiş sayılacağı, işçinin çalışma süresine göre İş Kanunu'nun 17. maddesinde şu şekilde düzenlenmiştir: altı aydan az çalışanlarda iki hafta, altı aydan birbuçuk yıla kadar çalışanlarda dört hafta, birbuçuk yıldan üç yıla kadar çalışanlarda altı hafta ve üç yıldan fazla çalışanlarda sekiz hafta [1]. Bu süreler asgari sürelerdir ve sözleşmelerle artırılabilir [1].

### openrouter:nvidia/nemotron-3-ultra-550b-a55b:free — c02: Gece çalışması en fazla kaç saat sürebilir?

_2.6 sn | atıflar: 4857 s. İş Kanunu m. 69 | geçersiz: []_

> İş Kanunu'na göre gece çalışması yedi buçuk saati geçemez [1]. Ancak turizm, özel güvenlik, sağlık hizmeti ve petrol araştırma/arama/sondaj faaliyetlerinde işçinin yazılı onayı alınması kaydıyla yedi buçuk saatin üzerinde gece çalışması yaptırılabilir [1].

### openrouter:nvidia/nemotron-3-ultra-550b-a55b:free — k01: İşveren işyerindeki güvenlik kamerasıyla ses kaydı alabilir mi?

_6.2 sn | atıflar: KVKK Kurulu K. 2023/2007 (Kurulun değerlendirmesi/1); KVKK Kurulu K. 2023/2007 (karar (hüküm)) | geçersiz: []_

> Hayır, işveren işyerindeki güvenlik kamerasıyla ses kaydı alamaz. Kurul, güvenlik amacıyla görüntü kaydı yeterli iken ilaveten ses kaydı alınmasında veri sorumlusunun meşru menfaatinin bulunmadığını, bu işlemenin Kanun'un 5. maddesindeki hiçbir işleme şartına dayanmadığını ve bu nedenle Kanun'un 12. maddesine aykırı olarak hukuka aykırı olduğunu kararlaştırmıştır [1][2]. Bu bağlamda veri sorumlusu hakkında idari para cezası uygulanmış ve hukuka aykırı olarak işlenen ses verilerinin imhası talimatlanmıştır [2].

### openrouter:nvidia/nemotron-3-ultra-550b-a55b:free — k03: Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyebilir mi?

_7.4 sn | atıflar: KVKK Kurulu K. 2023/426 (Kurulun değerlendirmesi/8); KVKK Kurulu K. 2023/426 (karar (hüküm)) | geçersiz: []_

> Hayır, mağaza taksitli satışta müşteriden e-Devlet şifresi isteyemez. [1][2]
> 
> KVKK Kurulu, finansman şirketinin taksitli alışverişlerde e-Devlet şifresi talep etmesinin, Kanun'un 5. maddesinde yer alan herhangi bir veri işleme şartına dayanmadığını ve bu nedenle veri sorumlusunun Kanun'un 12. maddesindeki güvenlik yükümlülüklerini ihlal ettiğini kararlaştırmıştır. [2]
> 
> Kurul, e-Devlet şifresi aracılığıyla hassas nitelikli veriler dahil pek çok kişisel veriye erişim sağlanabileceğine dikkat çekmiş ve bu uygulamanın hukuka aykırı olduğunu tespit ederek veri sorumlusu hakkında idari para cezası uygulamıştır. [1][2]

### openrouter:nvidia/nemotron-3-ultra-550b-a55b:free — r10: 2026 yılında net asgari ücret ne kadardır?

_2.8 sn | atıflar: — | geçersiz: []_

> CEVAP_YOK
> Verilen kaynaklarda 2026 yılına ilişkin net asgari ücret tutarı veya herhangi bir yıl için somut bir asgari ücret rakamı yer almamaktadır.

### openrouter:baidu/ernie-5.5-flash-preview:free — c01: İşçi iş sözleşmesini feshederken ne kadar önceden haber vermeli?

_0.1 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 400: Reasoning is mandatory for this endpoint and cannot be disabled.

### openrouter:baidu/ernie-5.5-flash-preview:free — c02: Gece çalışması en fazla kaç saat sürebilir?

_0.1 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 400: Reasoning is mandatory for this endpoint and cannot be disabled.

### openrouter:baidu/ernie-5.5-flash-preview:free — k01: İşveren işyerindeki güvenlik kamerasıyla ses kaydı alabilir mi?

_0.1 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 400: Reasoning is mandatory for this endpoint and cannot be disabled.

### openrouter:baidu/ernie-5.5-flash-preview:free — k03: Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyebilir mi?

_0.0 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 400: Reasoning is mandatory for this endpoint and cannot be disabled.

### openrouter:baidu/ernie-5.5-flash-preview:free — r10: 2026 yılında net asgari ücret ne kadardır?

_0.0 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 400: Reasoning is mandatory for this endpoint and cannot be disabled.

### openrouter:inclusionai/ling-3.0-flash — c01: İşçi iş sözleşmesini feshederken ne kadar önceden haber vermeli?

_2.3 sn | atıflar: 4857 s. İş Kanunu m. 17; 4857 s. İş Kanunu m. 24; 4857 s. İş Kanunu m. 26 | geçersiz: []_

> Süreli fesih hükümlerine göre işçi, iş sözleşmesini feshederken önceden bildirim yapmalıdır; bildirim süresi işçinin iş süresine göre değişir [1]. İşi altı aydan az sürmüş olan işçi için bildirimden başlayarak iki hafta sonra, altı aydan birbuçuk yıla kadar sürmüş olan işçi için dört hafta sonra, birbuçuk yıldan üç yıla kadar sürmüş olan işçi için altı hafta sonra ve üç yıldan fazla sürmüş işçi için sekiz hafta sonra feshedilmiş sayılır [1]. Bu süreler asgari olup sözleşmeyle artırılabilir [1]. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında tazminat ödemek zorundadır [1].
> 
> Ancak işçinin haklı nedenle derhal fesih hakkı mevcuttur [3]. Sağlık sebepleri, ahlak ve iyiniyet kurallarına uymayan haller ve zorlayıcı sebepler altında bildirim süresini beklemeksizin fesih yapılabilir [3]. Bu derhal fesih hakkının kullanım süresi, davranışın öğrendiği günden altı iş gün geçtikten ve fiilin gerçekleşmesinden itibaren bir yıl sonra kullanılamaz [5].

### openrouter:inclusionai/ling-3.0-flash — c02: Gece çalışması en fazla kaç saat sürebilir?

_1.3 sn | atıflar: 4857 s. İş Kanunu m. 69 | geçersiz: []_

> Gece çalışması süresi, 4857 sayılı İş Kanunu'nun 69. maddesi 3. fıkrasına göre işçilerin gece çalışmaları yedi buçuk saati geçemez [1]. Ancak turizm, özel güvenlik, sağlık hizmeti ve 6491 saylı Türk Petrol Kanunu uyarınca petrol araştırma, arama ve sondaj faaliyetleri kapsamında yürütülen işlerde işçinin yazılı onayının alınması şartıyla bu süre aşılarak gece çalışması yapılabileceği hükümler bulunmaktadır [1].

### openrouter:inclusionai/ling-3.0-flash — k01: İşveren işyerindeki güvenlik kamerasıyla ses kaydı alabilir mi?

_2.8 sn | atıflar: KVKK Kurulu K. 2023/2007 (Kurulun değerlendirmesi/1); KVKK Kurulu K. 2023/2007 (karar (hüküm)) | geçersiz: []_

> KVKK Kurulu, güvenlik kameralarının mevcut olmasına rağmen ilaveten ses kaydı almanın meşru menfaat gerektirmediğini ve bu nedenle hukuka aykırı olduğunu tespit etmiştir [1]. Bu doğrultuda, güvenlik kameralarıyla ses kaydı alınması suretiyle gerçekleştirilen kişisel veri işleme faaliyeti, Kanun’un 5’inci maddesindeki veri işleme şartlarından herhangi birine dayanılmamıştır [2]. Kurul, bu husus nedeniyle veri sorumlusuna 125.000 TL idari para cezası uygulanmasına karar vermiştir [2]. Ayrıca, hukuka aykırı olarak işlenen ses verilerinin imha edilmesi ve Kurula bilgi verilmesi talimatlandırılmıştır [2].

### openrouter:inclusionai/ling-3.0-flash — k03: Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyebilir mi?

_1.7 sn | atıflar: KVKK Kurulu K. 2023/426 (Kurulun değerlendirmesi/8); KVKK Kurulu K. 2023/426 (karar (hüküm)) | geçersiz: []_

> Mağaza taksitli satışta müşteriden e-Devlet şifresi talep etmesi, KVKK Kurulu kararı kapsamında hukuka aykırı işlem olarak değerlendirilmiştir [1][2]. Kararda, taksitli alışverişlerde e-Devlet şifresi talep edilmesinin Kanun'un 5'inci maddesinde yer alan herhangi bir veri işleme şartına dayanmadığı, dolayısıyla veri sorumlusunun Kanun'un 12'nci maddesinin (1) numaralı fıkrasındaki yükümlülüklerini yerine getirmediği belirtilmiştir [2]. Bu doğrultuda veri sorumlusuna 400.000 TL idari para cezası uygulanmıştır [2]. Ayrıca, ilgili kişilerin e-Devlet şifreleri talep edilerek hassas nitelikli kişisel veriler dahil pek çok kişiye veri erişimi sağlanabileceği göz önünde bulundurulmuştur [1][2]. Hukuka aykırı işlenen kişisel verilerin imha edilmesi ve sonucundan Kurula bilgi verilmesi karara konmuştur [2].

### openrouter:inclusionai/ling-3.0-flash — r10: 2026 yılında net asgari ücret ne kadardır?

_2.4 sn | atıflar: — | geçersiz: []_

> CEVAP_YOK
> Kaynaklarda 2026 yılı için asgari ücret tutarı bulunmamaktadır. Asgari Ücret Tespit Komisyonu kararları en geç iki yılda bir belirlenir ve Komisyon kararları kesindir; ancak kaynaklarda 2026 yılına ilişkin bir tutar verilmemiştir [1].

### openrouter:mistralai/mistral-nemo — c01: İşçi iş sözleşmesini feshederken ne kadar önceden haber vermeli?

_16.7 sn | atıflar: 4857 s. İş Kanunu m. 17 | geçersiz: []_

> [1] İş Kanunu'nun 17. maddesinin 2. fıkrasına göre, işçinin iş sözleşmesini feshedişi için bildirim yapması gerekmektedir. Bildirim süresi, işçinin işe alınma süresine bağlı olarak değişmektedir. İşçinin işe alınma süresi 6 ayın altındaysa bildirim süresi 2 haftadır; 6 ayın üstünde ve 1.5 yıldan az ise 4 haftadır; 1.5 yıldan 3 yıla kadar ise 6 haftadır; 3 yıldan fazla ise 8 haftadır. Bu süreler asgari olup, sözleşmeler ile artırılabilir.

### openrouter:mistralai/mistral-nemo — c02: Gece çalışması en fazla kaç saat sürebilir?

_1.2 sn | atıflar: — | geçersiz: []_

> Gece çalışması en fazla onbir saat sürebilir. [1/2]

### openrouter:mistralai/mistral-nemo — k01: İşveren işyerindeki güvenlik kamerasıyla ses kaydı alabilir mi?

_14.9 sn | atıflar: KVKK Kurulu K. 2023/2007 (Kurulun değerlendirmesi/1); KVKK Kurulu K. 2023/2007 (karar (hüküm)) | geçersiz: []_

> [1] ve [2] kaynaklarına göre, işveren işyerindeki güvenlik kamerasıyla görüntü kaydı almak hukuka uygun olabilir, ancak ses kaydı almak için Kanun'un 5. maddesinde yer alan veri işleme şartlarından herhangi birine dayanılmamış ve bu nedenle hukuka aykırı olarak işlenmiş olarak değerlendirilmiştir. Kurul, işverene 125.000 TL idari para cezası uygulayan kararı almıştır.

### openrouter:mistralai/mistral-nemo — k03: Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyebilir mi?

_16.8 sn | atıflar: KVKK Kurulu K. 2023/426 (Kurulun değerlendirmesi/8); KVKK Kurulu K. 2023/426 (karar (hüküm)) | geçersiz: []_

> [1] ve [2] kaynağında yer alan Kurul kararı, finansman şirketinin e-Devlet şifresi talep etmesi konusunda değerlendirmeler yapılmıştır. Ancak, bu kaynağın konusu yalnızca finansman şirketi ile ilgili ve e-Devlet şifresi talep etmesi konusunda değerlendirilen bir durumdur. Mevzuatın herhangi bir hükmü veya Kurul kararı, mağaza taksitli satışta müşteriden e-Devlet şifresi istememesini öngörmemiştir. Bu konuda mevzuatta bir hüküm yoktur. CEVAP_YOK

### openrouter:mistralai/mistral-nemo — r10: 2026 yılında net asgari ücret ne kadardır?

_5.3 sn | atıflar: — | geçersiz: []_

> CEVAP_YOK. Kaynaklar [1] ve [2] 2026 yılı için net asgari ücret hakkında bilgi vermez. Bu konu hakkında bilgi edinmek için daha güncel kaynaklara bakılması gerekmektedir.

### openrouter:qwen/qwen3.7-flash — c01: İşçi iş sözleşmesini feshederken ne kadar önceden haber vermeli?

_11.2 sn | atıflar: 4857 s. İş Kanunu m. 17; 4857 s. İş Kanunu m. 24; 4857 s. İş Kanunu m. 26 | geçersiz: []_

> Süresiz iş sözleşmelerinde işçinin fesih bildirimi yaparken uyması gereken süre, İş Kanunu'nun 17. maddesinde düzenlenen genel bildirim süresi kurallarına tabidir [1]. İşçinin işe başlama tarihi dikkate alınarak; altı aydan az çalışmışsa iki hafta, altı aydan birbuçuk yıla kadar sürmüşse dört hafta, birbuçuk yıldan üç yıla kadar sürmüşse altı hafta ve üç yıldan fazla çalışmışsa sekiz hafta önceden bildirimde bulunması gerekir [1]. Bu süreler asgari olup sözleşme ile artırılabilir [1]. Ancak, işçinin haklı nedenlere dayalı olarak derhal fesih hakkını kullanması halinde (örneğin ahlak ve iyi niyet kurallarına aykırı haller veya zorlayıcı sebepler), bildirim süresini beklemeden sözleşmeyi feshetmesi mümkündür [3]. Böyle bir durumda fesih yetkisi, davranışın öğrenildiği günden itibaren altı iş günü içinde kullanılmalıdır [5].

### openrouter:qwen/qwen3.7-flash — c02: Gece çalışması en fazla kaç saat sürebilir?

_3.0 sn | atıflar: 4857 s. İş Kanunu m. 69; 4857 s. İş Kanunu m. 41 | geçersiz: []_

> 4857 sayılı İş Kanunu’nun 69. maddesinin 3. fıkrasına göre, işçilerin gece çalışmaları yedibuçuk saati geçemez [1]. Ancak turizm, özel güvenlik, sağlık hizmeti ve petrol arama-arama-sondaj faaliyetleri gibi belirli işlerde, işçinin yazılı onayının alınması şartıyla bu süre aşılabilmektedir [1]. Ayrıca, gece çalışması yapılan hallerde fazla çalışma yapılamayacağından, gece çalışmasının süresi bu genel sınırlama ile belirlenir [4].

### openrouter:qwen/qwen3.7-flash — k01: İşveren işyerindeki güvenlik kamerasıyla ses kaydı alabilir mi?

_4.3 sn | atıflar: KVKK Kurulu K. 2023/2007 (Kurulun değerlendirmesi/1); KVKK Kurulu K. 2023/2007 (karar (hüküm)) | geçersiz: []_

> KVKK Kurulu’nun 2023/2007 sayılı kararında, işyerinde fiziksel mekan güvenliğinin sağlanması amacıyla kamera ile görüntü kaydı alınmasının meşru menfaat kapsamında olabileceği belirtilmekle birlikte, ilaveten ses kaydı alınmasında veri sorumlusunun meşru menfaatinin bulunmadığı ve bu işlemin zorunluluk şartını taşımadığı ifade edilmiştir [1]. Söz konusu kararda, güvenlik kameraları vasıtasıyla ses kaydı alınması suretiyle gerçekleştirilen kişisel veri işleme faaliyetinin Kanun’un 5’inci maddesinde yer alan herhangi bir veri işleme şartına dayanmadığına hükmedilmiştir [2]. Bu nedenle, işverenin işyerindeki güvenlik kameralarından sadece görüntü değil, aynı zamanda ses de kaydetmesi KVKK kapsamında hukuka uygun bulunmamaktadır [2].
> 
> CEVAP_YOK
> Kaynaklar yalnızca belirli bir Kurul kararının somut olaya yönelik değerlendirmesini içermekte olup, genel bir yasak veya istisnai durumları kapsayan evrensel bir yasal düzenlemeyi doğrudan metne aktarmamaktadır.

### openrouter:qwen/qwen3.7-flash — k03: Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyebilir mi?

_3.6 sn | atıflar: KVKK Kurulu K. 2023/426 (Kurulun değerlendirmesi/8); KVKK Kurulu K. 2023/426 (karar (hüküm)) | geçersiz: []_

> KVKK Kurulu, taksitli alışverişlerde müşterilerden e-Devlet şifresi talep edilmesinin Kanun’un 5’inci maddesinde yer alan herhangi bir veri işleme şartına dayanmadığına karar vermiştir [2]. Bu nedenle, veri sorumlusu tarafından e-Devlet şifrelerinin talep edilmesi hukuka aykırı kabul edilmekte ve idari para cezası uygulanmaktadır [2]. Kurul, bu tür taleplerin hassas nitelikli kişisel verilere de erişim sağlanmasına yol açabileceği gerekçesiyle işlemi yasaklayıcı bir yaklaşım sergilemiştir [1]. Dolayısıyla, mağaza taksitli satışlarında müşteriden e-Devlet şifresi istenmemelidir.

### openrouter:qwen/qwen3.7-flash — r10: 2026 yılında net asgari ücret ne kadardır?

_1.6 sn | atıflar: — | geçersiz: []_

> CEVAP_YOK
> Kaynaklarda 2026 yılına ait asgari ücret tutarı bulunmamaktadır; sadece asgari ücretin iki yılda bir belirleneceği ve komisyon kararlarının kesine olduğu belirtilmiştir [1].

### openrouter:z-ai/glm-5.3-flash — c01: İşçi iş sözleşmesini feshederken ne kadar önceden haber vermeli?

_0.2 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 400: Reasoning is mandatory for this endpoint and cannot be disabled.

### openrouter:z-ai/glm-5.3-flash — c02: Gece çalışması en fazla kaç saat sürebilir?

_0.1 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 400: Reasoning is mandatory for this endpoint and cannot be disabled.

### openrouter:z-ai/glm-5.3-flash — k01: İşveren işyerindeki güvenlik kamerasıyla ses kaydı alabilir mi?

_0.1 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 400: Reasoning is mandatory for this endpoint and cannot be disabled.

### openrouter:z-ai/glm-5.3-flash — k03: Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyebilir mi?

_0.1 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 400: Reasoning is mandatory for this endpoint and cannot be disabled.

### openrouter:z-ai/glm-5.3-flash — r10: 2026 yılında net asgari ücret ne kadardır?

_0.1 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 400: Reasoning is mandatory for this endpoint and cannot be disabled.

### openrouter:deepseek/deepseek-v4.1-flash-1017 — c01: İşçi iş sözleşmesini feshederken ne kadar önceden haber vermeli?

_2.6 sn | atıflar: 4857 s. İş Kanunu m. 17; 4857 s. İş Kanunu m. 24 | geçersiz: []_

> 4857 sayılı İş Kanunu'na göre süreli fesih için önce durumun diğer tarafa bildirilmesi gerekir ve bildirim süreleri işçinin kıdemine göre değişir [1]. İşçi, işi altı aydan az sürmüşse iki hafta, altı aydan bir buçuk yıla kadar sürmüşse dört hafta, bir buçuk yıldan üç yıla kadar sürmüşse altı hafta, üç yıldan fazla sürmüşse sekiz hafta sonra sözleşme feshedilmiş sayılır [1]. Bu süreler asgari olup sözleşmelerle artırılabilir [1]. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında tazminat ödemek zorundadır [1]. Ayrıca işçi, haklı nedenle derhal fesih hallerinde bildirim süresini beklemeksizin sözleşmeyi feshedebilir [3].

### openrouter:deepseek/deepseek-v4.1-flash-1017 — c02: Gece çalışması en fazla kaç saat sürebilir?

_2.2 sn | atıflar: 4857 s. İş Kanunu m. 69; 4857 s. İş Kanunu m. 41 | geçersiz: []_

> İşçilerin gece çalışmaları yedibuçuk saati geçemez [1]. Ancak turizm, özel güvenlik, sağlık hizmeti ve petrol araştırma, arama ve sondaj faaliyetleri kapsamında yürütülen işlerde işçinin yazılı onayının alınması şartıyla yedi buçuk saatin üzerinde gece çalışması yaptırılabilir [1]. Çalışma hayatında "gece", en geç saat 20.00'de başlayarak en erken saat 06.00'ya kadar geçen ve her halde en fazla onbir saat süren dönemdir [1]. Ayrıca gece çalışmasında fazla çalışma yapılamaz [4].

### openrouter:deepseek/deepseek-v4.1-flash-1017 — k01: İşveren işyerindeki güvenlik kamerasıyla ses kaydı alabilir mi?

_2.7 sn | atıflar: KVKK Kurulu K. 2023/2007 (Kurulun değerlendirmesi/1); KVKK Kurulu K. 2023/2007 (karar (hüküm)); KVKK Kurulu K. 2024/1361 (karar (hüküm)/2) | geçersiz: []_

> Kurul, bir olayda işverenin işyerinde kamera ile görüntü kaydı alınmasının güvenliği sağlama amacıyla bağdaştığını ve bu amaca yeterli olduğunu, buna karşılık ilaveten ses kaydı alınmasında veri sorumlusunun meşru menfaatinin bulunmadığını değerlendirmiştir [1]. Bu somut olayda güvenlik kulübesindeki kameralarla ses verilerinin işlenmesinde hukuka uygun bir işleme sebebi bulunmadığı belirtilmiştir [1]. Kurul, ses kaydı alınması suretiyle yapılan işleme faaliyetinin veri işleme şartlarından hiçbirine dayanmadığı, veri sorumlusunun gerekli teknik ve idari tedbirleri alma yükümlülüğünü ihlal ettiği gerekçesiyle idari para cezası uygulanmasına ve hukuka aykırı işlenen ses verilerinin imha edilmesine karar vermiştir [2]. Başka bir kararda ise güvenlik kameralarıyla ses kaydı alındığı iddiasının tevsik edilemediği, bu nedenle bu hususta işlem yapılmasına yer olmadığı; görüntü kaydı alınmasının ise hukuki yükümlülüğün yerine getirilmesi kapsamında hukuka uygun olduğu değerlendirilmiştir [5]. Bu kararlar somut olaylara özgüdür; genel kural olarak mevzuat hükümlerine bakılması gerekir.

### openrouter:deepseek/deepseek-v4.1-flash-1017 — k03: Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyebilir mi?

_2.4 sn | atıflar: KVKK Kurulu K. 2023/426 (Kurulun değerlendirmesi/8); KVKK Kurulu K. 2023/426 (karar (hüküm)) | geçersiz: []_

> Hayır, isteyemez. Kurul, bir finansman şirketinden yapılan taksitli alışverişlerde ilgili kişilerin e-Devlet şifrelerinin talep edildiğine dair şikâyetler üzerine yaptığı incelemede, e-Devlet şifrelerine erişim sağlandığı yönünde güçlü bir kanaat oluştuğunu ve bu yolla hassas nitelikli olanlar da dahil pek çok kişisel veriye erişilebileceğini belirtmiştir [1][2]. Bu somut olayda Kurul, e-Devlet şifresi talebinin Kanun'un 5'inci maddesindeki herhangi bir veri işleme şartına dayanmadığı ve veri güvenliğine ilişkin 12'nci maddedeki yükümlülüklerin yerine getirilmediği değerlendirmesiyle veri sorumlusuna idari para cezası uygulanmasına ve hukuka aykırı işlenen verilerin imha edilmesine karar vermiştir [2]. Bu, söz konusu olaya özgü bir Kurul kararıdır [1][2].

### openrouter:deepseek/deepseek-v4.1-flash-1017 — r10: 2026 yılında net asgari ücret ne kadardır?

_1.0 sn | atıflar: — | geçersiz: []_

> CEVAP_YOK
> Kaynaklarda 2026 yılına ait asgari ücret tutarına ilişkin herhangi bir bilgi bulunmamaktadır; yalnızca asgari ücretin belirlenme usulüne dair hükümler yer almaktadır [1].

### openrouter:openai/gpt-5-nano — c01: İşçi iş sözleşmesini feshederken ne kadar önceden haber vermeli?

_0.2 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 400: Reasoning is mandatory for this endpoint and cannot be disabled.

### openrouter:openai/gpt-5-nano — c02: Gece çalışması en fazla kaç saat sürebilir?

_0.1 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 400: Reasoning is mandatory for this endpoint and cannot be disabled.

### openrouter:openai/gpt-5-nano — k01: İşveren işyerindeki güvenlik kamerasıyla ses kaydı alabilir mi?

_0.1 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 400: Reasoning is mandatory for this endpoint and cannot be disabled.

### openrouter:openai/gpt-5-nano — k03: Mağaza taksitli satışta müşteriden e-Devlet şifresi isteyebilir mi?

_0.2 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 400: Reasoning is mandatory for this endpoint and cannot be disabled.

### openrouter:openai/gpt-5-nano — r10: 2026 yılında net asgari ücret ne kadardır?

_0.1 sn | atıflar: — | geçersiz: []_

> HATA: LLMError: OpenRouter 400: Reasoning is mandatory for this endpoint and cannot be disabled.

