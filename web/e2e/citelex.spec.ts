import { readFileSync } from "node:fs";
import path from "node:path";
import { expect, Page, test } from "@playwright/test";

import aciklamaVerisi from "./fixtures/aciklama.json";
import degisiklikVerisi from "./fixtures/degisiklikler.json";
import guncellikVerisi from "./fixtures/guncellik.json";
import ilgiliVerisi from "./fixtures/ilgili.json";
import kaynakVerileri from "./fixtures/kaynak.json";
import sorVerileri from "./fixtures/sor.json";

type SorAnahtar = keyof typeof sorVerileri;
type KaynakHaritasi = Record<string, (typeof kaynakVerileri)["is-kanunu:53"]>;
type DegisiklikHaritasi = Record<
  string,
  (typeof degisiklikVerisi.ayrintilar)["20261112T231836_karar_2023-2007_52-12"]
>;

const kaynakHaritasi = kaynakVerileri as unknown as KaynakHaritasi;
const degisiklikHaritasi = degisiklikVerisi.ayrintilar as unknown as DegisiklikHaritasi;

function soruSec(soru: string): (typeof sorVerileri)[SorAnahtar] {
  const kucuk = soru.toLocaleLowerCase("tr-TR");
  if (kucuk.includes("hava durumu")) return sorVerileri.bilmiyorum;
  if (kucuk.includes("depozito") || kucuk.includes("güvence")) return sorVerileri.genis_katman;
  if (kucuk.includes("parmak izi") || kucuk.includes("biyometrik")) return sorVerileri.ajan_deneme_2;
  return sorVerileri.yillik_izin;
}

function sseSonuc(veri: unknown, ajan: boolean): string {
  const j = veri as { cevap?: string; kaynaklar?: unknown[]; bilmiyorum?: boolean };
  if (!ajan && !j.bilmiyorum && typeof j.cevap === "string") {
    const baglam = `event: baglam\ndata: ${JSON.stringify({ kaynaklar: j.kaynaklar ?? [] })}\n\n`;
    const yarim = Math.floor(j.cevap.length / 2);
    const p1 = `event: parca\ndata: ${JSON.stringify({ metin: j.cevap.slice(0, yarim) })}\n\n`;
    const p2 = `event: parca\ndata: ${JSON.stringify({ metin: j.cevap.slice(yarim) })}\n\n`;
    const sonuc = `event: sonuc\ndata: ${JSON.stringify(veri)}\n\n`;
    return baglam + p1 + p2 + sonuc;
  }
  return `event: sonuc\ndata: ${JSON.stringify(veri)}\n\n`;
}

async function sahteApiKur(page: Page) {
  await page.route(
    (url) => url.pathname === "/guncellik" || url.pathname === "/saglik",
    async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json; charset=utf-8",
        body: JSON.stringify(guncellikVerisi),
      });
    },
  );

  await page.route(
    (url) => url.pathname === "/sor",
    async (route) => {
      const req = route.request();
      const url = new URL(req.url());
      const akisParam = url.searchParams.get("akis");
      let govde: { soru?: string; ajan?: boolean } = {};
      try {
        govde = JSON.parse(req.postData() ?? "{}") as { soru?: string; ajan?: boolean };
      } catch {
        govde = {};
      }
      const yanit = soruSec(govde.soru ?? "");
      if (akisParam === "false") {
        await route.fulfill({
          status: 200,
          contentType: "application/json; charset=utf-8",
          body: JSON.stringify(yanit),
        });
        return;
      }
      await route.fulfill({
        status: 200,
        headers: {
          "Content-Type": "text/event-stream; charset=utf-8",
          "Cache-Control": "no-cache",
        },
        body: sseSonuc(yanit, govde.ajan ?? true),
      });
    },
  );

  await page.route(
    (url) => url.pathname === "/kaynak",
    async (route) => {
      const url = new URL(route.request().url());
      const anahtar = url.searchParams.get("anahtar") ?? "";
      const veri = kaynakHaritasi[anahtar];
      if (!veri) {
        await route.fulfill({
          status: 404,
          contentType: "application/json; charset=utf-8",
          body: JSON.stringify({ detail: "Kaynak bulunamadı." }),
        });
        return;
      }
      await route.fulfill({
        status: 200,
        contentType: "application/json; charset=utf-8",
        body: JSON.stringify(veri),
      });
    },
  );

  await page.route(
    (url) => url.pathname === "/aciklama",
    async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json; charset=utf-8",
        body: JSON.stringify(aciklamaVerisi),
      });
    },
  );

  await page.route(
    (url) => url.pathname === "/ilgili",
    async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json; charset=utf-8",
        body: JSON.stringify(ilgiliVerisi),
      });
    },
  );

  await page.route(
    (url) => url.pathname === "/degisiklikler",
    async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json; charset=utf-8",
        body: JSON.stringify(degisiklikVerisi.liste),
      });
    },
  );

  await page.route(
    (url) => url.pathname.startsWith("/degisiklik/"),
    async (route) => {
      const url = new URL(route.request().url());
      const id = decodeURIComponent(url.pathname.slice("/degisiklik/".length));
      const ayrinti = degisiklikHaritasi[id];
      if (!ayrinti) {
        await route.fulfill({
          status: 404,
          contentType: "application/json; charset=utf-8",
          body: JSON.stringify({ detail: "Değişiklik bulunamadı." }),
        });
        return;
      }
      await route.fulfill({
        status: 200,
        contentType: "application/json; charset=utf-8",
        body: JSON.stringify(ayrinti),
      });
    },
  );
}

async function soruSor(page: Page, metin: string) {
  // Derlem güncelliği kartı yalnızca istemci hidrasyonu + /guncellik isteği tamamlandıktan sonra görünür
  await expect(page.getByRole("region", { name: "Derlem güncelliği" })).toBeVisible();
  const alan = page.getByLabel("Mevzuat sorunuz");
  await alan.fill(metin);
  await expect(alan).toHaveValue(metin);
  await page.getByRole("button", { name: /^Sor/ }).click();
}

test.describe("Citelex arayüz uçtan uca gerileme testleri (sahte API)", () => {
  test.beforeEach(async ({ page }) => {
    await sahteApiKur(page);
  });

  test("(1) soru -> cevap + [1] atıf -> kaynak paneli açılır, Esc kapatır ve odak geri döner (+ akis=false JSON)", async ({
    page,
  }) => {
    await page.goto("/");

    // akis=false JSON uç noktasının da aynı şemayla yanıt verdiğini doğrula
    const jsonYanit = await page.evaluate(async () => {
      const res = await fetch("/sor?akis=false", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ soru: "Yıllık izin kaç gündür?", ajan: true }),
      });
      return res.json();
    });
    expect(jsonYanit.bilmiyorum).toBe(false);
    expect(jsonYanit.kaynaklar[0].anahtar).toBe("is-kanunu:53");

    await soruSor(page, "Yıllık izin kaç gündür?");

    await expect(
      page.getByText(/yıllık ücretli izin verilir; izin süresi hizmet süresine göre 14, 20 veya 26/i),
    ).toBeVisible();

    const atifDugmesi = page.getByRole("button", {
      name: "Kaynak 1: 4857 s. İş Kanunu m. 53",
    });
    await expect(atifDugmesi).toBeVisible();
    await atifDugmesi.click();

    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();
    await expect(dialog.getByRole("heading", { name: "4857 s. İş Kanunu m. 53" })).toBeVisible();

    // Esc ile kapat ve odağın [1] atıf düğmesine döndüğünü doğrula
    await page.keyboard.press("Escape");
    await expect(dialog).toBeHidden();
    await expect(atifDugmesi).toBeFocused();
  });

  test("(2) İlişkili sekmesi -> İncele -> aynı panelde açılır ve geri düğmesiyle dönülür (+ Geçmiş tarihi)", async ({
    page,
  }) => {
    await page.goto("/");
    await soruSor(page, "Yıllık izin kaç gündür?");

    await page.getByRole("button", { name: "Kaynak 1: 4857 s. İş Kanunu m. 53" }).click();
    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();

    // Geçmiş sekmesinde Türkçe tarih biçimi
    await dialog.getByRole("tab", { name: /Geçmiş/ }).click();
    await expect(dialog.getByText("10 Eylül 2014")).toBeVisible();
    await expect(dialog.getByText("6552 s. Kanun md. 5")).toBeVisible();

    // İlişkili sekmesi: kısa atıf + başlık görünür, ham anahtar görünmez
    await dialog.getByRole("tab", { name: /İlişkili/ }).click();
    await expect(dialog.getByText("is-kanunu:10")).toHaveCount(0);
    await expect(dialog.getByText("4857 m. 10").first()).toBeVisible();
    await expect(dialog.locator("p", { hasText: "Sürekli ve süreksiz işlerdeki iş sözleşmeleri" })).toBeVisible();

    // "İncele →" tıklanınca aynı panelde m. 10 açılır
    await dialog
      .getByRole("button", { name: /4857 m\. 10.*Sürekli ve süreksiz işlerdeki iş sözleşmeleri/i })
      .click();
    await expect(dialog.getByRole("heading", { name: "4857 s. İş Kanunu m. 10" })).toBeVisible();

    const geriDugmesi = dialog.getByRole("button", {
      name: /Önceki maddeye dön \(4857 m\. 53\)/i,
    });
    await expect(geriDugmesi).toBeVisible();
    await geriDugmesi.click();

    await expect(dialog.getByRole("heading", { name: "4857 s. İş Kanunu m. 53" })).toBeVisible();
  });

  test("(3) Sade açıklama oluştur -> maddeler görünür", async ({ page }) => {
    await page.goto("/");
    await soruSor(page, "Yıllık izin kaç gündür?");

    await page.getByRole("button", { name: "Kaynak 1: 4857 s. İş Kanunu m. 53" }).click();
    const dialog = page.getByRole("dialog");
    await dialog.getByRole("tab", { name: "Sade açıklama" }).click();

    const olusturDugmesi = dialog.getByRole("button", { name: "Sade açıklama oluştur" });
    await expect(olusturDugmesi).toBeVisible();
    await olusturDugmesi.click();

    for (const madde of aciklamaVerisi.maddeler) {
      await expect(dialog.getByText(madde)).toBeVisible();
    }
    await expect(dialog.getByText(aciklamaVerisi.ornek)).toBeVisible();
  });

  test("(4) kapsam dışı soruda bilmiyorum kartı görünür", async ({ page }) => {
    await page.goto("/");
    await soruSor(page, "İstanbul'da bugün hava durumu nasıl?");

    await expect(page.getByText("Yetersiz kaynak / Kapsam dışı")).toBeVisible();
    await expect(page.getByText("Bu soruya elimdeki kaynaklarla cevap veremiyorum.")).toBeVisible();
    await expect(page.getByText("Soru, derlemdeki kaynaklara yeterince yakın değil.")).toBeVisible();
    await expect(page.getByRole("region", { name: "Atıfta bulunulan kaynaklar" })).toHaveCount(0);
  });

  test("(5) geniş katman rozeti ve uyarı metni yalnız tek kez görünür", async ({ page }) => {
    await page.goto("/");
    await soruSor(page, "Kira depozitosu en fazla kaç aylık kira olabilir?");

    await expect(page.getByText("Geniş katman · doğruluğu ölçülmedi")).toBeVisible();
    await expect(page.getByRole("article").getByText(/üç aylık kira bedelini aşamaz/i)).toBeVisible();

    const uyariCumleleri = page.getByText(/yaklaşık 900 kanun, Temmuz 2025'e kadar/i);
    await expect(uyariCumleleri).toHaveCount(1);
  });

  test("(6) ajan_deneme 2 olduğunda yeniden yazılan sorgu notu görünür", async ({ page }) => {
    await page.goto("/");
    await soruSor(page, "İşveren çalışanın parmak izini alabilir mi?");

    await expect(
      page.getByText(/2\. deneme:.*KVKK biyometrik veri parmak izi mesai takibi ölçülülük/i),
    ).toBeVisible();

    await page.getByRole("button", { name: /Bu cevap nasıl oluştu\?/i }).click();
    await expect(page.getByText("Derin arama denemesi")).toBeVisible();
    await expect(page.getByText("2. deneme", { exact: true })).toBeVisible();
  });

  test("(7) API kapalı olduğunda kullanıcıya anlaşılır hata mesajı gösterilir", async ({ page }) => {
    await page.route(
      (url) => url.pathname === "/sor",
      async (route) => {
        await route.abort("connectionrefused");
      },
    );

    await page.goto("/");
    await soruSor(page, "Yıllık izin kaç gündür?");

    const alert = page.getByRole("alert").filter({ hasText: "API sunucusuna ulaşılamadı." });
    await expect(alert).toBeVisible();
  });

  test("(8) /pano yüklenir ve üst kartlar pano.json ile birebir tutarlıdır", async ({ page }) => {
    const panoYolu = path.join(__dirname, "..", "public", "pano.json");
    const panoJson = JSON.parse(readFileSync(panoYolu, "utf-8")) as {
      modeller: Array<{
        dogru: number;
        n_ic: number;
        dogru_orani: number;
        dogru_ret: number;
        n_dis: number;
        dogru_ret_orani: number;
        sadakat?: {
          tam_destekli: number;
          cevap: number;
          tam_destekli_orani: number;
        } | null;
      }>;
    };

    const enIyi = [...panoJson.modeller].sort((a, b) => b.dogru_orani - a.dogru_orani)[0];
    expect(enIyi).toBeTruthy();

    await page.goto("/pano/");
    await expect(page.getByRole("heading", { name: "Değerlendirme panosu" })).toBeVisible();

    const ozetBolumu = page.getByRole("region", { name: "Öne çıkan metrikler" });
    await expect(ozetBolumu).toContainText(`%${Math.round(enIyi.dogru_orani * 100)}`);
    await expect(ozetBolumu).toContainText(`${enIyi.dogru}/${enIyi.n_ic}`);
    await expect(ozetBolumu).toContainText(`${enIyi.dogru_ret}/${enIyi.n_dis}`);
    if (enIyi.sadakat) {
      await expect(ozetBolumu).toContainText(`%${Math.round(enIyi.sadakat.tam_destekli_orani * 100)}`);
      await expect(ozetBolumu).toContainText(`${enIyi.sadakat.tam_destekli}/${enIyi.sadakat.cevap}`);
    }
  });

  test("(9) /degisiklikler kelime farkı görünümü ve yan yana geçiş çalışır", async ({ page }) => {
    await page.goto("/degisiklikler/");
    await expect(page.getByRole("heading", { name: "Bu madde değişti" })).toBeVisible();

    const ayrinti = page.getByRole("region", { name: "Değişiklik ayrıntısı" });
    await expect(ayrinti).toBeVisible();
    await expect(ayrinti.getByRole("heading", { name: "KVKK Kurul Kararı 2023/2007" })).toBeVisible();

    // Satır içi fark sekmesinde silinen (175.000) ve eklenen (125.000) kelimeler
    await expect(ayrinti.locator("del", { hasText: "175.000" })).toBeVisible();
    await expect(ayrinti.locator("ins", { hasText: "125.000" })).toBeVisible();

    // Yan yana (Eski / Yeni metin) görünümüne geçiş
    await ayrinti.getByRole("button", { name: "Eski / Yeni metin" }).click();
    await expect(ayrinti.getByText(/Eski metin · Sürüm #52/i)).toBeVisible();
    await expect(ayrinti.getByText(/Yeni metin · Sürüm #12/i)).toBeVisible();
  });

  test("(10) 390px mobil genişlikte tüm sayfalarda yatay taşma yoktur (scrollWidth <= innerWidth)", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    const rotalar = ["/", "/pano/", "/degisiklikler/", "/yontem/", "/gelistirici/"];

    for (const rota of rotalar) {
      await page.goto(rota);
      await expect(page.locator("main")).toBeVisible();
      const olcum = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        innerWidth: window.innerWidth,
      }));
      expect(
        olcum.scrollWidth,
        `${rota} sayfasında yatay taşma: scrollWidth=${olcum.scrollWidth} > innerWidth=${olcum.innerWidth}`,
      ).toBeLessThanOrEqual(olcum.innerWidth);
    }
  });

  test("(11) tema anahtarı açık/koyu geçişini yapar ve sayfa yenilendiğinde kalıcıdır", async ({
    page,
  }) => {
    await page.goto("/");

    const ilkTema = await page.evaluate(() => document.documentElement.getAttribute("data-tema"));
    const temaDugmesi = page
      .getByRole("button", { name: /Koyu temaya geç|Açık temaya geç/i })
      .first();
    await temaDugmesi.click();

    const yeniTema = ilkTema === "dark" ? "light" : "dark";
    await expect(page.locator("html")).toHaveAttribute("data-tema", yeniTema);

    const depoDegeri = await page.evaluate(() => localStorage.getItem("citelex:tema"));
    expect(depoDegeri).toBe(yeniTema);

    await page.reload();
    await expect(page.locator("html")).toHaveAttribute("data-tema", yeniTema);
  });
});
