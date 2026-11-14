"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { SiteKabugu } from "@/components/SiteKabugu";
import { ModelOzeti, PanoVerisi, kisaModelAdi, yuzde } from "@/components/pano/types";

function modelBul(modeller: ModelOzeti[], yapilandirma: string, llmIcerir = "deepseek"): ModelOzeti | undefined {
  return modeller.find((m) => m.yapilandirma === yapilandirma && m.llm.includes(llmIcerir));
}

export default function YontemSayfasi() {
  const [veri, setVeri] = useState<PanoVerisi | null>(null);
  const [hata, setHata] = useState<string | null>(null);

  useEffect(() => {
    fetch("/pano.json")
      .then((res) => {
        if (!res.ok) throw new Error("pano.json yüklenemedi.");
        return res.json() as Promise<PanoVerisi>;
      })
      .then((d) => setVeri(d))
      .catch((e) => setHata((e as Error).message));
  }, []);

  const modeller = veri?.modeller ?? [];
  const dsTek = modelBul(modeller, "tek_adim");
  const dsAjan = modelBul(modeller, "ajan");
  const dsRerankAjan = modelBul(modeller, "reranker+ajan");
  const tekAdimModeller = modeller.filter((m) => m.yapilandirma === "tek_adim" && m.sadakat != null);
  const rerank = veri?.rerank_karsilastirma;
  const genisAcik = veri?.genis_katman?.acik_eval?.[0];
  const genisArama = veri?.genis_katman?.arama;

  return (
    <SiteKabugu aktif="yontem" baslikAlt="Nasıl çalışır ve ölçüm sınırları">
      <div className="space-y-6">
        <section className="space-y-2">
          <span className="text-[11px] font-semibold tracking-wider text-accent uppercase">
            Mimari ve Metodoloji
          </span>
          <h1 className="font-serif text-3xl font-medium tracking-tight text-ink">
            Yöntem ve sınırlar
          </h1>
          <p className="text-sm leading-relaxed text-muted">
            Citelex, Türk mevzuatı ve KVKK Kurul kararları için geliştirilmiş kaynak doğrulamalı bir RAG
            uygulamasıdır. Aşağıdaki özetlerin tüm sayıları canlı{" "}
            <Link href="/pano/" prefetch={false} className="text-accent underline underline-offset-4">
              pano.json
            </Link>{" "}
            verisinden okunur.
          </p>
        </section>

        {hata && (
          <p role="alert" className="rounded-xl border border-warn-border bg-warn-bg px-4 py-3 text-xs text-warn-ink">
            {hata}
          </p>
        )}

        <section aria-labelledby="yontem-katmanlar" className="space-y-3 rounded-xl border border-line bg-panel p-5 shadow-xs">
          <h2 id="yontem-katmanlar" className="font-serif text-xl font-medium text-ink">
            1. İki katmanlı mevzuat derlemi
          </h2>
          <div className="grid gap-3 text-xs leading-relaxed sm:grid-cols-2">
            <div className="space-y-1.5 rounded-xl border border-line bg-bg/60 p-4">
              <div className="font-semibold text-ink">Derin katman (ölçülür)</div>
              <p className="text-muted">
                KVKK, İş Kanunu (4857 ve 1475 m. 14), İSG Kanunu (6331), ilgili yönetmelik/tebliğler ile 40 KVKK Kurul
                kararı. Mevzuat (5 yer) ve Kurul kararları (en çok 3 karar) ayrı kanallarda aranır; her cümle [n]
                atıfıyla doğrulanır.
              </p>
            </div>
            <div className="space-y-1.5 rounded-xl border border-line bg-bg/60 p-4">
              <div className="font-semibold text-ink">Geniş katman (~900 kanun · ölçülmedi)</div>
              <p className="text-muted">
                Derin katman yoğun skor eşiğinin (0,637) altında kaldığında veya geniş katman üstünlüğü 0,05 farkı
                aştığında devreye giren yedek kanaldır. Cevapların doğruluğu tam setle ölçülmediği için arayüzde uyarı
                rozeti gösterilir.
              </p>
            </div>
          </div>
        </section>

        <section aria-labelledby="yontem-bilmiyorum" className="space-y-3 rounded-xl border border-line bg-panel p-5 shadow-xs">
          <h2 id="yontem-bilmiyorum" className="font-serif text-xl font-medium text-ink">
            2. &ldquo;Bilmiyorum&rdquo; eşiği ve ajan modu
          </h2>
          <p className="text-sm leading-relaxed text-muted">
            Kapsam dışı sorularda uydurma cevap vermemek için üç aşamalı koruma uygulanır: (1) arama yoğun skor eşiği
            (0,637), (2) modelin kaynak yetersizliğinde döndürdüğü <code>CEVAP_YOK</code> kararı ve (3) atıf
            doğrulaması (kaynak listesi dışındaki [n] atıfları elenir).
          </p>

          {(dsTek || dsAjan || dsRerankAjan) && (
            <div className="w-full overflow-x-auto rounded-xl border border-line">
              <table className="w-full border-collapse text-left text-xs sm:text-sm">
                <thead>
                  <tr className="border-b border-line bg-bg/50 text-xs text-muted">
                    <th className="px-3.5 py-2 font-medium">Yapılandırma</th>
                    <th className="px-3.5 py-2 text-right font-medium">Doğru</th>
                    <th className="px-3.5 py-2 text-right font-medium">Yanlış ret</th>
                    <th className="px-3.5 py-2 text-right font-medium">Kapsam dışı ret</th>
                    <th className="px-3.5 py-2 text-right font-medium">Geçersiz atıf</th>
                    <th className="px-3.5 py-2 text-right font-medium">Medyan süre</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line tabular-nums">
                  {[dsTek, dsAjan, dsRerankAjan].filter((x): x is ModelOzeti => Boolean(x)).map((m) => (
                    <tr key={m.anahtar} className="hover:bg-bg/60">
                      <td className="px-3.5 py-2 font-medium text-ink">
                        {kisaModelAdi(m.llm)} · {m.yapilandirma_adi}
                      </td>
                      <td className="px-3.5 py-2 text-right font-semibold text-ink">
                        {yuzde(m.dogru_orani)} ({m.dogru}/{m.n_ic})
                      </td>
                      <td className="px-3.5 py-2 text-right text-muted">
                        {m.yanlis_ret}/{m.n_ic}
                      </td>
                      <td className="px-3.5 py-2 text-right text-ink">
                        {m.dogru_ret}/{m.n_dis}
                      </td>
                      <td className="px-3.5 py-2 text-right text-ink">{m.gecersiz_atif}</td>
                      <td className="px-3.5 py-2 text-right text-muted">
                        {m.medyan_sure_sn != null ? `${m.medyan_sure_sn.toFixed(2).replace(".", ",")} sn` : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <p className="text-xs leading-relaxed text-muted">
            API&apos;de varsayılan olarak <strong>derin arama (ajan) modu açıktır</strong>; yalnız ilk aramada eşik
            altında kalan veya yetersiz dönen sorularda sorgu bir kez yeniden yazılıp aranır.{" "}
            <code>bge-reranker-v2-m3</code> CPU yayınında gecikme nedeniyle varsayılan kapalı tutulur.
          </p>
        </section>

        <section aria-labelledby="yontem-sadakat" className="space-y-3 rounded-xl border border-line bg-panel p-5 shadow-xs">
          <h2 id="yontem-sadakat" className="font-serif text-xl font-medium text-ink">
            3. Kaynak sadakati (LLM hakem)
          </h2>
          <p className="text-sm leading-relaxed text-muted">
            Anahtar kelime eşleşmesi doğru cevabı ölçmekte tek başına yeterli değildir; cevaptaki her iddianın atıf
            yaptığı metinle desteklenip desteklenmediği <code>claude-haiku-5.5</code> hakemiyle ayrıca ölçülür
            (hakem kararları 10 örnekte elle incelenmiş ve 9/10 uyum görülmüştür).
          </p>

          {tekAdimModeller.length > 0 && (
            <div className="w-full overflow-x-auto rounded-xl border border-line">
              <table className="w-full border-collapse text-left text-xs sm:text-sm">
                <thead>
                  <tr className="border-b border-line bg-bg/50 text-xs text-muted">
                    <th className="px-3.5 py-2 font-medium">Model (tek adım)</th>
                    <th className="px-3.5 py-2 text-right font-medium">Anahtar kelime doğru</th>
                    <th className="px-3.5 py-2 text-right font-medium">Tam destekli cevap</th>
                    <th className="px-3.5 py-2 text-right font-medium">Destekli iddia</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line tabular-nums">
                  {tekAdimModeller.map((m) => (
                    <tr key={m.anahtar} className="hover:bg-bg/60">
                      <td className="px-3.5 py-2 font-medium text-ink">{kisaModelAdi(m.llm)}</td>
                      <td className="px-3.5 py-2 text-right text-ink">
                        {m.dogru}/{m.n_ic} ({yuzde(m.dogru_orani)})
                      </td>
                      <td className="px-3.5 py-2 text-right font-semibold text-ink">
                        {m.sadakat!.tam_destekli}/{m.sadakat!.cevap} ({yuzde(m.sadakat!.tam_destekli_orani)})
                      </td>
                      <td className="px-3.5 py-2 text-right text-muted">{yuzde(m.sadakat!.destekli_orani)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {rerank && rerank.satirlar.length > 0 && (
            <p className="text-xs leading-relaxed text-muted">
              Reranker (<code>{rerank.dosya}</code>): <code>bge-reranker-v2-m3</code> yalnız sıralama ölçümünde mevzuat
              R@1 değerini {rerank.satirlar[0]?.r1} → {rerank.satirlar[1]?.r1} / {rerank.satirlar[0]?.n} ve MRR değerini{" "}
              {rerank.satirlar[0]?.mrr.toFixed(3).replace(".", ",")} →{" "}
              {rerank.satirlar[1]?.mrr.toFixed(3).replace(".", ",")} düzeyine çıkardı.
            </p>
          )}
        </section>

        <section aria-labelledby="yontem-sinirlar" className="space-y-3 rounded-xl border border-line bg-panel p-5 shadow-xs">
          <h2 id="yontem-sinirlar" className="font-serif text-xl font-medium text-ink">
            4. Bilinen sınırlar
          </h2>
          <ul className="list-disc space-y-2 pl-5 text-xs leading-relaxed text-muted">
            <li>
              <strong className="text-ink">Taslak altın etiketler:</strong> 56 soruluk derin katman seti ile{" "}
              {genisArama ? `${genisArama.sorular.length} soruluk ` : ""}geniş katman taslak soru setinin beklenen
              cevapları hukuki doğrulama bekler; kalibrasyon eşiği (0,637) test setine değil ayrı kalibrasyon setine göre
              ayarlanmıştır.
            </li>
            <li>
              <strong className="text-ink">Geniş katman kapsama alanı:</strong>{" "}
              {genisAcik?.kapsam_disi
                ? `Geniş katman açıkken kapsam dışı ret ${genisAcik.kapsam_disi} olmuştur (d03 7036 s. Kanun m. 3). `
                : ""}
              Trafik cezası veya şirket kuruluşu gibi bazı genel hukuk soruları geniş katmana girse bile tüm sorular
              kapsamlı doğrulanmamıştır.
            </li>
            <li>
              <strong className="text-ink">Ücretsiz model zinciri gecikmesi:</strong> OpenRouter ücretsiz katmanı günlük
              kotaya ulaştığında devre kesici bir sonraki modele geçer; kalite ve yanıt süresi seçili aktif modele göre
              değişebilir.
            </li>
            <li>
              <strong className="text-ink">Hukuki tavsiye değildir:</strong> Sistem yalnızca getirilen mevzuat ve Kurul
              kararlarını özetler; somut uyuşmazlıklarda resmî metinden teyit edilmelidir.
            </li>
          </ul>
        </section>
      </div>
    </SiteKabugu>
  );
}
