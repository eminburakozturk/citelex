# Citelex Masaüstü ve Mobil İstemci (Tauri 2)

`desktop/` klasörü, `web/out` statik Next.js çıktısını paketleyen **ince istemci** Tauri 2 projesidir. Model, gömme veya Qdrant indeksi cihazda bulunmaz; uygulama yalnızca derleme sırasında belirlenen bulut/yerel API adresine istek atar.

- **Uygulama adı:** `Citelex` (`com.citelex.client`)
- **Pencere boyutu (masaüstü):** Varsayılan `1200x800`, minimum `400x600`

---

## Önkoşullar

- **Node.js** 22+ (`web/` statik derlemesi için)
- **Rust + Cargo** (`rustc 1.77+`) ve **Tauri CLI**: `cargo install tauri-cli --locked`
- **Android için ek olarak:** Android SDK (`ANDROID_HOME`), NDK (`NDK_HOME`), JDK (`JAVA_HOME`) ve Rust Android hedefleri (`rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android x86_64-linux-android`)

---

## API Adresi (`NEXT_PUBLIC_API_URL`)

`cargo tauri build` ve `cargo tauri android build`, `beforeBuildCommand` olarak [build-web.mjs](build-web.mjs) üzerinden `web/` projesini derler. API adresi **derleme zamanında** `NEXT_PUBLIC_API_URL` ortam değişkeninden alınır (varsayılan: `http://127.0.0.1:8000`).

Örnek (PowerShell):

```powershell
$env:NEXT_PUBLIC_API_URL = "https://api.example.com"
```

---

## Derleme Komutları

`desktop/` dizini içinden çalıştırın:

### Windows (EXE / MSI / NSIS)

```powershell
cd desktop
cargo tauri build
```

Çıktılar:
- `src-tauri/target/release/citelex.exe`
- `src-tauri/target/release/bundle/msi/Citelex_0.1.0_x64_en-US.msi`
- `src-tauri/target/release/bundle/nsis/Citelex_0.1.0_x64-setup.exe`

### Android (Release APK, ABI başına bölünmüş)

İlk seferde proje üretmek için:

```powershell
cd desktop
cargo tauri android init --ci --skip-targets-install
```

Yerel keystore'u **repo dışında** tutarak (`C:\Users\Burak\.citelex\citelex-release.jks`) oluşturma ve imzalı release derleme:

```powershell
# Anahtar deposu oluşturma (tek seferlik, şifreyi repo içine yazmayın)
& "$env:JAVA_HOME\bin\keytool.exe" -genkeypair -v `
  -keystore C:\Users\Burak\.citelex\citelex-release.jks `
  -alias citelex -keyalg RSA -keysize 2048 -validity 10000

# Ortam değişkenleriyle release APK derleme
$env:CITELEX_KEYSTORE_PATH = "C:\Users\Burak\.citelex\citelex-release.jks"
$env:CITELEX_KEY_ALIAS = "citelex"
$env:CITELEX_KEYSTORE_PASSWORD = "<keystore-sifresi>"
$env:CITELEX_KEY_PASSWORD = "<key-sifresi>"

cd desktop
cargo tauri android build --apk --split-per-abi
```

`CITELEX_KEYSTORE_PATH` / `CITELEX_KEYSTORE_PASSWORD` tanımlı değilse [build.gradle.kts](src-tauri/gen/android/app/build.gradle.kts) imzasız release APK üretir (`*-release-unsigned.apk`). Debug imzalı test derlemesi için `cargo tauri android build --apk --debug` kullanılabilir.

---

## Sunucu CORS Ayarı (`CITELEX_CORS`)

Tauri webview'u işletim sistemine göre farklı kökenlerden istek gönderir. `src/api/app.py` servisinin çalıştığı sunucuda `CITELEX_CORS` ortam değişkenine Tauri kökenlerini ekleyin:

```text
CITELEX_CORS=http://localhost:3000,tauri://localhost,http://tauri.localhost,https://tauri.localhost
```

---

## Bilinen Sınırlar

- **Çevrimdışı çalışma yok:** İnce istemci tüm sorgular için API sunucusuna ihtiyaç duyar; API adresi derleme sonrasında çalışma zamanında değiştirilemez.
- **Release APK'da HTTP (`cleartext`) kapalı:** Android `release` yapısında `usesCleartextTraffic=false` olduğu için gerçek cihazlarda bulut API'nin `https://` ile sunulması gerekir (`http://127.0.0.1` telefon içinde yalnızca cihazın kendisine işaret eder; emülatörde host makineye erişmek için `http://10.0.2.2:8000` yalnızca `debug` derlemede `usesCleartextTraffic=true` ile çalışır).
- **Android edge-to-edge üst çubuk:** Android 15+/API 37 cihazlarda sistem durum çubuğu üst başlıkla hafifçe çakışabilir (`web/` içine `safe-area-inset-top` boşluğu henüz eklenmemiştir).
- **İmza ve mağaza dağıtımı:** Yerel `.jks` kendinden imzalıdır; Google Play Store dağıtımı gerektirirseniz Play App Signing / geliştirici hesabı ayrıca yapılandırılmalıdır.
