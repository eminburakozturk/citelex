import type { NextConfig } from "next";

// Statik çıktı (out/): aynı dosyalar web'de ve Tauri (EXE/APK) içinde çalışır; sunucu tarafı yok.
// API adresi derleme anında NEXT_PUBLIC_API_URL ile verilir (anahtar DEĞİL; anahtar yalnız API sunucusunda).
const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
