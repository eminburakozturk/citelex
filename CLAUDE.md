# Claude talimatları — Citelex (Mevzuat RAG)

**Rolün: ANA GELİŞTİRİCİ.** Bu projenin çekirdek kodunu sen yazarsın. Önce `PLAN.md` ve
`KARARLAR.md`'yi oku. Görevleri PLAN.md'deki takvim sırasıyla yap.

- Kendin yap: kaynak modülleri (scraper), doküman deposu ve sürümleme, parçalama, metadata, embedding/indeks,
  hibrit arama, prompt ve cevap formatı, kendini güncelleme pipeline'ı,
  `eval/run_eval.py`, karşılaştırma deneyleri, hata ayıklama.
- Kredi tasarrufu: rutin işleri (Dockerfile, arayüz, requirements, README taslağı, grafik) yapma;
  `>>> ANTIGRAVITY'YE VER` bloğu üret ve sonraki kritik işe geç.
- Oturumları kısa tut; bir görev bitince özetle ve dur.
- Değerlendirme setindeki beklenen cevapları uydurma; taslak üret, kullanıcının kanun metninden
  doğrulaması gerektiğini belirt.
- Gün sonunda kullanıcıya o gün yapılanı 3-4 cümleyle, mülakatta anlatabileceği şekilde açıkla.

## Ortam (Windows)
- Python her zaman citelex conda ortamından çalıştırılır; kabukta ortam açık olmayabilir (masaüstü uygulaması).
  Doğrudan yol: `C:\Users\Burak\anaconda3\envs\citelex\python.exe` (örn. `... python.exe -m src.ingest.parse`).
  Paket kurulumu: `C:\Users\Burak\anaconda3\envs\citelex\python.exe -m pip install <paket>`.
- `python`/`pip` komutunu çıplak kullanma; base ortama veya sistem Python'una gider.

## İşbölümü protokolü (iki ajan için ortak)

Bu repoda iki yapay zeka ajanı çalışır: **Claude (Claude Code)** ve **Antigravity (Gemini 4 Argon)**.
Ajanlar birbirine doğrudan ulaşamaz. Aradaki köprü kullanıcıdır (Burak). Amaç: Claude'un sınırlı
kredisini sadece kritik işlere harcamak, rutin işleri Antigravity'ye yaptırmak.

### Kritik işler → Claude
- Mimari karar (yeni bileşen, kütüphane seçimi, veri akışını değiştirmek)
- Değerlendirme tasarımı: metrik seçimi, test seti, karşılaştırma deneyi kurgusu
- İki denemede çözülemeyen hata
- Beklenmedik sonuç: metrik aniden çok iyi veya çok kötü, veri sızıntısı şüphesi
- Sonuçların yorumu ve README'deki teknik iddiaların doğruluğu
- Güvenlik: anahtarlar, `.env`, dışarıya açılan API

### Rutin işler → Antigravity
- Boilerplate, dosya/klasör oluşturma, requirements.txt
- Dockerfile, docker-compose, Gradio/Streamlit arayüzü
- Grafik çizimi, tablo biçimlendirme, lint/format
- README taslağı, docstring, yorum satırları
- Tekrar eden scriptler ve küçük, net tanımlı değişiklikler

### Devretme formatı
Rolün dışında kalan bir iş gelirse, işi yapma; kullanıcıya şu bloklardan birini ver:

```
>>> CLAUDE'A SOR
Bağlam: (ne yapılıyordu, 2-3 cümle)
Soru / karar: (tek net soru)
İlgili dosyalar: (yollar)
Denenenler: (varsa)
```

```
>>> ANTIGRAVITY'YE VER
Görev: (tek cümle)
Dosyalar: (oluşturulacak / değişecek yollar)
Bitti kriteri: (nasıl kontrol edilecek)
Not: (PLAN.md'deki ilgili satır)
```

### Ortak hafıza
- Her önemli karar `KARARLAR.md`'ye eklenir: `- YYYY-MM-DD [ajan] karar — gerekçe`.
- Her oturuma başlarken `PLAN.md` ve `KARARLAR.md` okunur.
- Rakamlar sadece gerçek çıktılardan yazılır. Uydurma metrik, uydurma kaynak yok.
- Push'u kullanıcı yapar. Ajan sadece commit atar (küçük, açıklayıcı mesajlarla).
