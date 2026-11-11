// KVKK karar özeti sayfasından gürültüsüz metin çıkarıcı (tarayıcıda, kvkk.gov.tr kökeninde çalışır).
// kvkk.gov.tr otomatik istemcileri anasayfaya yönlendirdiği için (KARARLAR.md, 2026-11-11) karar metinleri
// uygulama içi tarayıcıda bu fonksiyonla çıkarıldı; metin + SHA-256 panoya JSON olarak kopyalanıp
// diske hash doğrulamasıyla yazıldı. Çıktı biçimi:
//   BAŞLIK: ... / KAYNAK: url / Yayınlanma Tarihi: ... / (boş) / Karar Tarihi, Karar No, Konu Özeti /
//   paragraflar (boş satırla ayrık) ve "- " ile başlayan liste maddeleri.
// İçerik kabı: .news__detail-article. Eski sayfalarda içerik bir DIV sarmalayıcının içinde; walk() iner.
const norm = s => s.replace(/[ \t \r\n]+/g, ' ').trim();

async function kvExtract(url) {
  const d = new DOMParser().parseFromString(await (await fetch(url)).text(), 'text/html');
  const a = d.querySelector('.news__detail-article');
  if (!a) return null;
  const head = d.querySelector('.news__detail-head');
  const out = [];
  let title = '';
  const walk = (el) => {
    for (const c of el.children) {
      const tg = c.tagName;
      if (tg === 'H2' && !title) title = norm(c.textContent);
      else if (tg === 'TABLE') {
        for (const tr of c.querySelectorAll('tr'))
          out.push([...tr.children].map(x => norm(x.textContent)).filter(Boolean).join(' ').replace(/\s*:\s*/, ': '));
        out.push('');
      } else if (tg === 'UL' || tg === 'OL') {
        for (const li of c.querySelectorAll(':scope > li')) out.push('- ' + norm(li.textContent));
        out.push('');
      } else if ((tg === 'DIV' || tg === 'SECTION' || tg === 'ARTICLE') && c.querySelector('p,table,ul,ol,div')) walk(c);
      else { const t = norm(c.textContent); if (t) out.push(t, ''); }
    }
  };
  walk(a);
  const txt = ['BAŞLIK: ' + title, 'KAYNAK: https://www.kvkk.gov.tr' + url, head ? norm(head.textContent) : '', '', ...out]
    .join('\n').replace(/\n{3,}/g, '\n\n').trim() + '\n';
  const sha = [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(txt)))]
    .map(b => b.toString(16).padStart(2, '0')).join('');
  return { txt, sha, len: txt.length };
}
