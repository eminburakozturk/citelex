# Claude talimatları — Citelex (Mevzuat RAG)

**Rolün: TEK GELİŞTİRİCİ.** Projenin tamamı sende (2026-11-12 kullanıcı kararı; başka ajana iş
devredilmez). Önce `PLAN.md` ve `KARARLAR.md`'yi oku. Görevleri PLAN.md'deki takvim sırasıyla yap.

- Kapsam: kaynak modülleri (scraper), doküman deposu ve sürümleme, parçalama, metadata, embedding/indeks,
  hibrit arama, prompt ve cevap formatı, kendini güncelleme pipeline'ı, değerlendirme ve karşılaştırma
  deneyleri, FastAPI, Gradio arayüzü, Dockerfile/docker-compose, requirements, README, grafikler, hata ayıklama.
- Rutin işleri (boilerplate, arayüz, Docker, README biçimi) sade ve hızlı yap; zamanı ve krediyi
  kritik işlere (mimari, değerlendirme, sonuçların doğruluğu, güvenlik) ayır.
- Oturumları kısa tut; bir görev bitince özetle ve dur.
- Değerlendirme setindeki beklenen cevapları uydurma; derlem metninden taslak üret, kullanıcının kanun
  metninden doğrulaması gerektiğini belirt.
- Gün sonunda kullanıcıya o gün yapılanı 3-4 cümleyle, mülakatta anlatabileceği şekilde açıkla.

## Kullanıcıya sorulacaklar
Şunlarda işi durdur ve kullanıcıya tek net soru sor:
- Kapsamı veya PLAN.md takvimini değiştiren kararlar
- Ödünleşimi ürün tercihi olan kararlar (ör. "bilmiyorum" eşiği: daha çok cevap mı, daha az yanlış mı)
- Siteye erişim engeli, elle indirme veya hesap/kota/faturalama gerektiren durumlar
- Beklenmedik sonuç: metrik aniden çok iyi veya çok kötü, veri sızıntısı şüphesi

## Ortam (Windows)
- Python her zaman citelex conda ortamından çalıştırılır; kabukta ortam açık olmayabilir (masaüstü uygulaması).
  Doğrudan yol: `C:\Users\Burak\anaconda3\envs\citelex\python.exe` (örn. `... python.exe -m src.ingest.parse`).
  Paket kurulumu: `C:\Users\Burak\anaconda3\envs\citelex\python.exe -m pip install <paket>`.
- `python`/`pip` komutunu çıplak kullanma; base ortama veya sistem Python'una gider.
- Qdrant Docker'da (`citelex-qdrant`, restart=unless-stopped). Bağlantı reddedilirse önce Docker Desktop'ın
  açık olduğunu kontrol et; değilse başlat ve `docker start citelex-qdrant`.

## Ortak hafıza
- Her önemli karar `KARARLAR.md`'ye eklenir: `- YYYY-MM-DD [claude|kullanıcı] karar — gerekçe`.
- Her oturuma başlarken `PLAN.md` ve `KARARLAR.md` okunur.
- Rakamlar sadece gerçek çıktılardan yazılır. Uydurma metrik, uydurma kaynak yok.
- Push'u kullanıcı yapar. Ajan sadece commit atar (küçük, açıklayıcı mesajlarla).
