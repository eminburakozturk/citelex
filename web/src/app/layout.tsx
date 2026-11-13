import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Citelex — Kaynak gösteren mevzuat asistanı",
  description:
    "KVKK, İş Kanunu ve İSG mevzuatı üzerine soru-cevap. Her cevap madde atfı ve güncellik tarihiyle gelir. Hukuki tavsiye değildir.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr" className="h-full antialiased">
      <body className="h-full">{children}</body>
    </html>
  );
}
