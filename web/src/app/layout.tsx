import type { Metadata, Viewport } from "next";
import { Inter, Newsreader } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin", "latin-ext"],
  variable: "--font-inter",
  display: "swap",
});

const newsreader = Newsreader({
  subsets: ["latin", "latin-ext"],
  variable: "--font-newsreader",
  style: ["normal", "italic"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Citelex — Türk mevzuatı için kaynak gösteren soru-cevap",
  description:
    "KVKK, İş Kanunu, İSG Kanunu, KVKK Kurul kararları ve genel kanun derleminde madde atıflı mevzuat arama ve soru-cevap.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

const TEMA_BASLANGIC = `(function(){try{var t=localStorage.getItem('citelex:tema');if(t==='light'||t==='dark'){document.documentElement.setAttribute('data-tema',t);}}catch(e){}})();`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr" className={`${inter.variable} ${newsreader.variable}`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: TEMA_BASLANGIC }} />
      </head>
      <body className="min-h-screen bg-bg text-ink antialiased selection:bg-accent-soft selection:text-accent">
        {children}
      </body>
    </html>
  );
}
