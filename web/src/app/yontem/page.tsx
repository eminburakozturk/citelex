"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ModelOzeti, PanoVerisi, kisaModelAdi, tarihSaat, yuzde } from "@/components/pano/types";

const ADIMLAR = [
  {
    no: "1",
    baslik: "İki kanallı arama",
    ozet:
      "Mevzuat (en çok 5 aday) ve KVKK Kurul kararları (en çok 3 karardan 2'şer parça) Qdrant'ta ayrı aranır. Her kanalda bge-m3 dense + Türkçe BM25 sparse sonuçları RRF (k=60) ile birleştirilir; mülga ve başka kanuna işlenmiş hükümler dışlanır.",
    detay:
      "Mevzuat fıkra düzeyinde aranıp tam maddeye genişletilir (3000+ karakterde eşleşen fıkra ±1). Kararlar herhangi bir bölümden eşleşir, ancak bağlama yalnız Kurulun değerlendirmesi ve hüküm bölümleri girer.",
  },
  {
    no: "2",
    baslik: "Eşik kapısı",
    ozet:
      "Dense en iyi skor (top-1) 0,637 eşiğinin altındaysa sistem kaynak uydurmak yerine \"bilmiyorum\" döner. Bu eşik değerlendirme setinden ayrı 30 soruluk kalibrasyon setinde seçilmiştir.",
    detay:
      "Aynı eşik kanal bazında da uygulanır; böylece ilgisiz mevzuat veya karar parçalarının bağlama girip küçük modelleri yanıltması engellenir.",
  },
  {
    no: "3",
    baslik: "Üretim (LLM)",
    ozet:
      "OpenRouter model zinciri (veya yerel Ollama) temperature=0 ile yalnızca numaralı kaynaklardan yanıt üretir. Kaynak yetersizse model ilk satıra CEVAP_YOK yazar.",
    detay:
      "Tek adımlı modda cevap parça parça (SSE) akar; ajan modunda ek değerlendirme yapıldığı için doğrulanmış tek sonuç döner.",
  },
  {
    no: "4",
    baslik: "Atıf doğrulama",
    ozet:
      "Üretilen metindeki [n] atıflarının her biri verilen kaynak listesiyle eşleştirilir. Var olmayan numaralar ayıklanır; geçerli atfı kalmayan cevap reddedilerek \"bilmiyorum\"a çevrilir.",
    detay:
      "Bu adım geçersiz veya uydurma madde numarası riskini (ölçülen çalıştırmalarda 0 geçersiz atıf) kapatır.",
  },
  {
    no: "5",
    baslik: "LangGraph ajan (varsayılan açık)",
    ozet:
      "Yalnız eşik altı veya CEVAP_YOK durumunda devreye girer. Soruyu Türk mevzuatı terimleriyle (ör. biyometrik veri, ilgili kanun adı) bir arama sorgusuna çevirip en fazla 1 kez daha arar.",
    detay:
      "İkinci aramanın kaynakları ilkiyle birleştirilir; cevap yine özgün soruya yazılır ve aynı atıf doğrulamasından geçer.",
  },
];

const SINIRLAR = [
  "56 soruluk değerlendirme setindeki beklenen cevaplar taslaktır (hukuki doğrulama bekler); içerik puanı anahtar kelime eşleşmesine dayanır.",
  "0,637 eşiği \"daha az yanlış cevap\" yönünde tutucudur; kısa veya genel kapsam içi soruları kesebilir (ajan modu bu darboğazı büyük ölçüde aşar).",
  "Atıf geçerliliği anlamsal doğruluğu tek başına kanıtlamaz; bu yüzden iddia düzeyi sadakat LLM hakemiyle ayrıca ölçülür.",
  "Derin katman 12 mevzuat belgesi ve 40 seçili KVKK Kurul kararıyla sınırlıdır. Geniş katman (895 kanun, 44.854 parça) arama kapsamındadır ancak doğruluğu henüz ölçülmemiştir.",
  "Örneklem küçüktür (eval 56 soru, arama deneyleri 63 soru); 1–2 soruluk farklar gürültü sınırındadır.",
];

function satirBul(modeller: ModelOzeti[], llmIcerir: string, yapilandirma: string): ModelOzeti | undefined {
  return modeller.find((m) => m.llm.includes(llmIcerir) && m.yapilandirma === yapilandirma);
}

export default function YontemSayfasi() {
  const [veri, setVeri] = useState<PanoVerisi | null>(null);
  const [hata, setHata] = useState<string | null>(null);

  useEffect(() => {
    let iptal = false;
    fetch("/pano.json")
      .then((res) => {
        if (!res.ok) throw new Error("pano.json yüklenemedi.");
        return res.json() as Promise<PanoVerisi>;
      })
      .then((json) => {
        if (!iptal) setVeri(json);
      })
      .catch((e: Error) => {
        if (!iptal) setHata(e.message);
      });
    return () => {
      iptal = true;
    };
  }, []);

  const dsTek = veri ? satirBul(veri.modeller, "deepseek", "tek_adim") : undefined;
  const dsRerank = veri ? satirBul(veri.modeller, "deepseek", "reranker") : undefined;
  const dsAjan = veri ? satirBul(veri.modeller, "deepseek", "ajan") : undefined;
  const nemotronTek = veri ? satirBul(veri.modeller, "nemotron", "tek_adim") : undefined;
  const qwenTek = veri ? satirBul(veri.modeller, "qwen3.7", "tek_adim") : undefined;
  const localTek = veri ? satirBul(veri.modeller, "qwen2.5", "tek_adim") : undefined;

  const rerankMevzuat = veri?.rerank_karsilastirma?.satirlar.filter((s) => s.kanal === "mevzuat") ?? [];
  const hibritDense = veri?.arama_deneyleri?.parcalama_yontem.find(
    (s) => s.parcalama === "hibrit" && s.yontem === "dense"
  );
  const hibritRrf = veri?.arama_deneyleri?.parcalama_yontem.find(
    (s) => s.parcalama === "hibrit" && s.yontem === "hybrid"
  );
  const sozcuksel = veri?.arama_deneyleri?.sozcuksel ?? [];

  return (
    <div className="min-h-full overflow-x-hidden bg-bg text-ink">
      <header className="guvenli-ust guvenli-yatay border-b border-line bg-panel pb-3">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-between gap-x-4 gap-y-1">
          <h1 className="text-lg font-semibold tracking-tight">
            Citelex <span className="font-normal text-muted">· Yöntem ve mimari özeti</span>
          </h1>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted">
            {veri?.uretim_tarihi && <span>Ölçüm verisi: {tarihSaat(veri.uretim_tarihi)}</span>}
            <Link href="/pano" className="inline-flex min-h-[40px] items-center text-accent hover:underline">
              Değerlendirme panosu
            </Link>
            <Link href="/degisiklikler" className="inline-flex min-h-[40px] items-center text-accent hover:underline">
              Son değişiklikler
            </Link>
            <Link href="/" className="inline-flex min-h-[40px] items-center text-accent hover:underline">
              ← Soru-cevaba dön
            </Link>
          </div>
        </div>
      </header>

      <main className="guvenli-sayfa-alt guvenli-yatay mx-auto max-w-4xl min-w-0 space-y-8 pt-6">
        <section className="space-y-2 rounded-lg border border-line bg-panel p-4">
          <h2 className="text-base font-semibold">Bu sistem neyi farklı yapıyor?</h2>
          <p className="text-sm leading-relaxed text-ink">
            Citelex, Türk mevzuatı (KVKK, İş Kanunu, İSG Kanunu, ilgili yönetmelik/tebliğler ve 40 seçili KVKK Kurul
            kararı) üzerinde yalnızca doğrulanmış kaynak parçalarından yanıt üretir. Kaynak metinler değiştiğinde farkı
            madde/bölüm düzeyinde yakalayıp yalnızca değişen parçaları yeniden indeksler; kanıt yetmediğinde uydurma
            yerine <strong>&ldquo;bilmiyorum&rdquo;</strong> der.
          </p>
          <p className="text-xs text-muted">
            Tasarım ilkeleri: <code>KARARLAR.md</code> · Sayısal sonuçlar doğrudan <code>web/public/pano.json</code>{" "}
            dosyasından okunur.
          </p>
        </section>

        <section aria-labelledby="genis-katman-baslik" className="space-y-1.5 rounded-lg border border-line bg-panel p-4">
          <h2 id="genis-katman-baslik" className="text-sm font-semibold text-ink">
            Geniş katman (~900 kanun) ne zaman devreye girer?
          </h2>
          <p className="text-sm leading-relaxed text-ink">
            Yalnızca derin katman (KVKK, İş Kanunu, İSG Kanunu, ilgili yönetmelik/tebliğler ve 40 Kurul kararı) kalibre
            edilmiş <code>0,637</code> eşiğini geçemezse ve tür filtresi kanunu kapsıyorsa <code>citelex_genis</code>{" "}
            koleksiyonu (895 kanun, 44.854 parça, Temmuz 2025&apos;e kadar) aranır; derin katman sorularının davranışı
            değişmez. Geniş katmanın doğruluğu ve güncelliği eval setiyle ölçülmediği için yanıtlar rozet ve resmî
            metinden kontrol uyarısıyla döner.
          </p>
        </section>

        <section aria-labelledby="nasil-calisir-baslik" className="space-y-3">
          <h2 id="nasil-calisir-baslik" className="text-base font-semibold">
            1. Sistem nasıl çalışır?
          </h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {ADIMLAR.map((a) => (
              <article key={a.no} className="space-y-1.5 rounded-lg border border-line bg-panel p-4">
                <div className="flex items-center gap-2">
                  <span className="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent-soft text-xs font-semibold text-accent">
                    {a.no}
                  </span>
                  <h3 className="text-sm font-semibold text-ink">{a.baslik}</h3>
                </div>
                <p className="text-sm leading-relaxed text-ink">{a.ozet}</p>
                <p className="text-xs leading-relaxed text-muted">{a.detay}</p>
              </article>
            ))}
          </div>
        </section>

        <section aria-labelledby="nasil-olculur-baslik" className="space-y-3">
          <h2 id="nasil-olculur-baslik" className="text-base font-semibold">
            2. Nasıl ölçülür?
          </h2>
          <div className="grid gap-3 md:grid-cols-3">
            <article className="space-y-1.5 rounded-lg border border-line bg-panel p-4">
              <h3 className="text-sm font-semibold text-ink">56 soruluk eval seti</h3>
              <p className="text-xs leading-relaxed text-muted">
                50 kapsam içi (mevzuat ve karar) ve 6 kapsam dışı soruda bağlam isabeti, atıf isabeti, içerik anahtar
                kelimesi, yanlış &ldquo;bilmiyorum&rdquo; katmanı ve geçersiz atıf sayısı ölçülür. Eşik ayrı 30 soruluk
                kalibrasyon setinde sabitlenir.
              </p>
            </article>
            <article className="space-y-1.5 rounded-lg border border-line bg-panel p-4">
              <h3 className="text-sm font-semibold text-ink">LLM hakemli sadakat</h3>
              <p className="text-xs leading-relaxed text-muted">
                <code>anthropic/claude-haiku-5.5</code> hakemi her cevabı iddialara bölüp kaynak metne göre denetler. Asıl
                ölçüt <em>tam destekli</em> orandır (kısmen ve desteksiz iddia yok). 10 kararlık elle kontrolde 9 uyum
                görülmüştür.
              </p>
            </article>
            <article className="space-y-1.5 rounded-lg border border-line bg-panel p-4">
              <h3 className="text-sm font-semibold text-ink">CI arama kapısı</h3>
              <p className="text-xs leading-relaxed text-muted">
                GitHub Actions her değişiklikte <code>eval/gate.py</code> ile bellekte Türkçe BM25 aramasını (63
                beklenen kaynaklı soru) koşar; mevzuat 48/51 veya karar 12/12 temelinin altına düşerse derleme başarısız
                olur.
              </p>
            </article>
          </div>
        </section>

        <section aria-labelledby="onemli-sonuclar-baslik" className="space-y-3">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h2 id="onemli-sonuclar-baslik" className="text-base font-semibold">
              3. En önemli sonuçlar
            </h2>
            <Link href="/pano" className="inline-flex min-h-[40px] items-center text-xs text-accent hover:underline">
              Tüm tablo ve soru ısı haritasını gör →
            </Link>
          </div>

          {hata && <p className="rounded-md border border-line bg-panel px-3 py-2 text-sm text-accent">{hata}</p>}
          {!veri && !hata && <p className="text-sm text-muted">Sonuçlar pano.json&apos;dan yükleniyor…</p>}

          {veri && (
            <div className="grid gap-3 md:grid-cols-2">
              {dsAjan && dsTek && (
                <article className="space-y-1.5 rounded-lg border border-line bg-panel p-4">
                  <h3 className="text-sm font-semibold text-ink">Ajan modu darboğazı aştı (varsayılan açık)</h3>
                  <p className="text-sm text-ink tabular-nums">
                    <strong>{kisaModelAdi(dsAjan.llm)}</strong> tek adımda{" "}
                    <strong>
                      {dsTek.dogru}/{dsTek.n_ic} ({yuzde(dsTek.dogru_orani)})
                    </strong>{" "}
                    iken ajanla{" "}
                    <strong>
                      {dsAjan.dogru}/{dsAjan.n_ic} ({yuzde(dsAjan.dogru_orani)})
                    </strong>
                    ; yanlış &ldquo;bilmiyorum&rdquo; {dsTek.yanlis_ret} → {dsAjan.yanlis_ret}.
                  </p>
                  <p className="text-xs text-muted tabular-nums">
                    Kapsam dışı ret {dsAjan.dogru_ret}/{dsAjan.n_dis}, geçersiz atıf {dsAjan.gecersiz_atif}, medyan{" "}
                    {dsAjan.medyan_sure_sn?.toFixed(2)} sn
                    {dsAjan.sadakat
                      ? `, tam destekli sadakat ${dsAjan.sadakat.tam_destekli}/${dsAjan.sadakat.cevap} (${yuzde(dsAjan.sadakat.tam_destekli_orani)})`
                      : ""}
                    .
                  </p>
                </article>
              )}

              {dsTek && nemotronTek && qwenTek && (
                <article className="space-y-1.5 rounded-lg border border-line bg-panel p-4">
                  <h3 className="text-sm font-semibold text-ink">Sadakat hakemi modelleri ayırıyor</h3>
                  <p className="text-sm text-ink tabular-nums">
                    Tek adımda doğruluklar yakınken ({kisaModelAdi(dsTek.llm)} {dsTek.dogru}/{dsTek.n_ic},{" "}
                    {kisaModelAdi(nemotronTek.llm)} {nemotronTek.dogru}/{nemotronTek.n_ic},{" "}
                    {kisaModelAdi(qwenTek.llm)} {qwenTek.dogru}/{qwenTek.n_ic}), tam destekli sadakat sırasıyla{" "}
                    <strong>{yuzde(dsTek.sadakat?.tam_destekli_orani)}</strong>,{" "}
                    <strong>{yuzde(nemotronTek.sadakat?.tam_destekli_orani)}</strong> ve{" "}
                    <strong>{yuzde(qwenTek.sadakat?.tam_destekli_orani)}</strong>.
                  </p>
                  <p className="text-xs text-muted tabular-nums">
                    {localTek
                      ? `Yerel ${kisaModelAdi(localTek.llm)}: ${localTek.dogru}/${localTek.n_ic} (${yuzde(localTek.dogru_orani)}) doğru, ${localTek.yanlis_ret} yanlış ret.`
                      : ""}
                  </p>
                </article>
              )}

              {rerankMevzuat.length >= 2 && (
                <article className="space-y-1.5 rounded-lg border border-line bg-panel p-4">
                  <h3 className="text-sm font-semibold text-ink">Reranker sırayı iyileştirir ama CPU&apos;da yavaştır</h3>
                  <p className="text-sm text-ink tabular-nums">
                    Mevzuatta ({rerankMevzuat[0].n} soru) {rerankMevzuat[0].yontem} R@1={rerankMevzuat[0].r1}, MRR=
                    {rerankMevzuat[0].mrr.toFixed(3)} → {rerankMevzuat[1].yontem} R@1={rerankMevzuat[1].r1}, MRR=
                    {rerankMevzuat[1].mrr.toFixed(3)}.
                  </p>
                  <p className="text-xs text-muted tabular-nums">
                    {dsRerank
                      ? `Uçtan uca bağlam ${dsRerank.baglam}/${dsRerank.n_ic}'ya çıksa da eşik darboğazı yüzünden doğru ${dsRerank.dogru}/${dsRerank.n_ic} kaldı (medyan ${dsRerank.medyan_sure_sn?.toFixed(2)} sn); CPU yayında kapalı.`
                      : ""}
                  </p>
                </article>
              )}

              {hibritDense && hibritRrf && (
                <article className="space-y-1.5 rounded-lg border border-line bg-panel p-4">
                  <h3 className="text-sm font-semibold text-ink">Arama katmanı bulguları</h3>
                  <p className="text-sm text-ink tabular-nums">
                    Hibrit parçalamada dense (mevzuat R@1 {hibritDense.mevzuat_r1}, MRR{" "}
                    {hibritDense.mevzuat_mrr.toFixed(3)}), hibrit RRF&apos;den (R@1 {hibritRrf.mevzuat_r1}, MRR{" "}
                    {hibritRrf.mevzuat_mrr.toFixed(3)}) {`2`} soru öndedir; soru seti derlemden üretildiği için dense&apos;i
                    kayırabilir.
                  </p>
                  <p className="text-xs text-muted tabular-nums">
                    {sozcuksel.length >= 2
                      ? `Sözcüksel kanal: ${sozcuksel[0].yontem} R@1 ${sozcuksel[0].r1} (MRR@5 ${sozcuksel[0].mrr5.toFixed(3)}) vs ${sozcuksel[1].yontem} R@1 ${sozcuksel[1].r1} (MRR@5 ${sozcuksel[1].mrr5.toFixed(3)}).`
                      : ""}
                  </p>
                </article>
              )}
            </div>
          )}
        </section>

        <section aria-labelledby="sinirlar-baslik" className="space-y-3">
          <h2 id="sinirlar-baslik" className="text-base font-semibold">
            4. Bilinen sınırlar
          </h2>
          <ul className="space-y-2 rounded-lg border border-line bg-panel p-4 text-sm text-ink">
            {SINIRLAR.map((s) => (
              <li key={s} className="flex gap-2">
                <span className="text-accent" aria-hidden="true">
                  •
                </span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </section>
      </main>
    </div>
  );
}
