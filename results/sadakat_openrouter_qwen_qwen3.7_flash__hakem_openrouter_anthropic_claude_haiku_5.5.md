# Sadakat (LLM hakem) — openrouter_qwen_qwen3.7_flash

Hakem: openrouter_anthropic_claude_haiku_5.5 (talimat v2) | cevap: 42 (hata 0) | iddia: 162 | hakem maliyeti: $0.0309

Yalnız cevap verilen kapsam içi sorular. Hakem kaynak metnine göre etiketler; kendi hukuk bilgisini kullanmaz (talimat). Hakem de hata yapabilir: elle kontrol örneklemi KARARLAR.md'de. Kısmen/desteksiz sınırı koşudan koşuya oynayabildiği için asıl ölçüt 'tam destekli'dir.

| Ölçüt | Değer |
|---|---|
| **Tam destekli cevap** (kısmen/desteksiz iddia yok) | 26/42 (%62) |
| Desteksiz iddiası olmayan cevap | 38/42 (%90) |
| Destekli iddia | 145/162 (%90) |
| Kısmen | 13 |
| Desteksiz | 4 |
| Uyarı cümlesi (sayılmadı) | 4 |

## Anahtar kelime ölçütüyle (`dogru`) ayrışanlar

| # | dogru (anahtar) | tam destekli (hakem) | Kısmen/desteksiz iddialar |
|---|---|---|---|
| e06 | ✓ | ✗ | [kismen] Kesinti yapılan paralar, bir ay içinde Çalışma ve Sosyal Güvenlik Bakanlığı hesabına yatır — Kaynakta paralar bir ay içinde Bakanlık hesabına değil, Bakanlıkça belirtilecek ve mevduat |
| e10 | ✓ | ✗ | [kismen] Ancak, işçi onsekiz yaşından küçük veya elli yaşından büyük ise izin süresi yirmi günden a — Kaynaklarda onsekiz ve daha küçük yaştaki ile elli ve daha yukarı yaştaki işçiler için yir |
| e11 | ✓ | ✗ | [kismen] Dolayısıyla, izin süresinin parçalara ayrılması durumunda her bir parça on günden az süre  — Kaynaklarda 'bir bölümü on günden aşağı olmamak üzere' ifadesi var; ancak her bir parçanın |
| e14 | ✓ | ✗ | [kismen] Bu dinlenme süresi en az bir saattir ve aralıksız olarak kullandırılır. — Kaynak [1] dinlenme sürelerinin en az olup aralıksız verileceğini söylüyor (68/2); ancak y |
| e17 | ✓ | ✗ | [desteksiz] Dolayısıyla işçinin talep edebileceği tazminat, maddi ve manevi zararları ile dört aya kad — Kaynak 5. madde 6. fıkrada yalnızca 'dört aya kadar ücreti tutarında uygun bir tazminat' i |
| e25 | ✗ | ✓ | — |
| e26 | ✓ | ✗ | [kismen] Bu ilkeler, 6698 sayılı Kanun’un 4. maddesinde genel ilkeler olarak düzenlenmiştir [5]. — Kaynak [5] 4. maddedeki ilkeleri aktarıyor ancak 6698 sayılı Kanun numarasını açıkça belir; [kismen] Kurul kararlarında da bu hususların veri işleme faaliyetlerinin hukuka uygunluğu açısından — Kaynak [7] ölçülülük ve ilkelere uyumu değerlendiriyor ancak bu ilkelerin hukuka uygunluğu |
| e30 | ✓ | ✗ | [desteksiz] Bu durum, başvurunun sonuçsuz kaldığına dair hukuki bir sonuc doğurur ancak başvuru sahibi — Verilen kaynak metinlerinde mahkeme yoluna başvuru hakkı ya da red sayılmanın diğer haklar |
| e36 | ✓ | ✗ | [kismen] Bu kural, işlemin ayrıca bir maliyet gerektirmesi hâlinde Kurulca belirlenen tarifedeki üc — Kaynak [2] ve [3], işlemin ayrıca maliyet gerektirmesi hâlinde ücret alınabileceğini söylü |
| e38 | ✓ | ✗ | [kismen] KVKK Kurulu, iş akdinin sonlandırılmasına ilişkin duyurunun şirketin herkese açık sosyal m — Kaynaklarda idari para cezası ve imha kararı var; ancak kaynaklar olayın 'iş akdinin sonla |
| e41 | ✓ | ✗ | [kismen] Ayrıca, biyometrik veri işlenmesinin “ölçülü olma” ilkesine de aykılık teşkil ettiği belir — Ölçülülük ilkesine aykırılık kaynakta var; ancak kaynakta 'işlemi iptal eden' bir karar ye |
| e43 | ✓ | ✗ | [kismen] Kişisel Verileri Koruma Kurulunun 2024/592 sayılı kararına göre, banka çalışanı telefon gö — Kaynaklar, Kanun'un 11. maddesi kapsamında talep edilen telefon görüşme kayıtlarının üçünc |
| e44 | ✓ | ✗ | [desteksiz] Evet, Kurul bu konuda işlem yapmıştır. — Kaynaklar Kurulun işlem yaptığını değil, 'veri sorumlusu hakkında Kanun kapsamında yapılac |
| e45 | ✓ | ✗ | [kismen] İlgili kişinin maddi tazminat talebi için yargı yoluna başvurulabileceğine dair de bilgi v — Kaynaklar, veri sorumlusunun ilgili kişinin maddi tazminat ödenmesi durumunda Kurula şikây |
| e47 | ✓ | ✗ | [desteksiz] Aynı çalışma alanında birden fazla işverenin bulunması halinde de bu koordinasyon hükümler — Atıf yapılan [3] (30. madde) yönetmeliklerin konularını düzenliyor; aynı çalışma alanında  |
