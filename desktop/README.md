# Citelex Masaüstü ve Mobil İstemci (Tauri 2)

`desktop/` klasörü, `web/out` statik Next.js çıktısını `desktop/dist` içine kopyalayıp paketleyen **ince istemci** Tauri 2 projesidir (derleme sonunda `web/out` otomatik olarak `NEXT_PUBLIC_API_URL=same-origin` ile geri derlenir). Model, gömme veya Qdrant indeksi cihazda bulunmaz; uygulama yalnızca derleme sırasında belirlenen bulut/yerel API adresine istek atar.

- **Uygulama adı:** `Citelex` (`com.citelex.client`)
- **Pencere boyutu (masaüstü):** Varsayılan `1200x800`, minimum `400x600`

---

## Önkoşullar

- **Node.js** 22+ (`web/` statik derlemesi için)
- **Rust + Cargo** (`rustc 1.77+`) ve **Tauri CLI**: `cargo install tauri-cli --locked`
- **Android için ek olarak:** Android SDK (`ANDROID_HOME`), NDK (`NDK_HOME`), JDK (`JAVA_HOME`) ve Rust Android hedefleri (`rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android x86_64-linux-android`)

---

## API Adresi (`NEXT_PUBLIC_API_URL`)

`cargo tauri build` ve `cargo tauri android build`, `beforeBuildCommand` olarak [build-web.mjs](build-web.mjs) üzerinden `web/` projesini derler, çıktıyı `desktop/dist/` altına alır ve ardından `web/out/` dizinini Docker sunumu için `NEXT_PUBLIC_API_URL=same-origin` ile geri yükler. API adresi **derleme zamanında** `NEXT_PUBLIC_API_URL` ortam değişkeninden alınır (varsayılan: `http://127.0.0.1:8000`). Özel bir API adresi kullanıldığında [csp-config.mjs](csp-config.mjs) ile CSP politikasındaki `connect-src` kökeni üretilip `--config src-tauri/tauri.csp.json` ile verilmelidir:

Örnek (PowerShell):

```powershell
$env:NEXT_PUBLIC_API_URL = "https://api.example.com"
node csp-config.mjs
cargo tauri build --config src-tauri/tauri.csp.json
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

## Telefona kurulum

1. **Derleme zamanı API adresi:** Gerçek telefon `127.0.0.1` ile sunucuya ulaşamaz. Derlemeden önce bulut (veya HTTPS) API adresini verin:

```powershell
$env:NEXT_PUBLIC_API_URL = "https://api.example.com"
cd desktop
node csp-config.mjs
cargo tauri android build --apk --split-per-abi --config src-tauri/tauri.csp.json
```

2. **USB hata ayıklama ve kurulum:** Telefonda **Geliştirici Seçenekleri → USB Hata Ayıklama** ayarını açın, USB ile bağlayın ve `arm64-v8a` APK'yı yükleyin (birden fazla cihaz bağlıysa `adb devices` çıktısındaki seri numarasını `-s` ile belirtin):

```powershell
& "$env:ANDROID_HOME\platform-tools\adb.exe" devices
& "$env:ANDROID_HOME\platform-tools\adb.exe" install -r `
  src-tauri/gen/android/app/build/outputs/apk/arm64/release/app-arm64-release.apk
```

3. **Emülatörde yerel API (`10.0.2.2:8000`) testi:** Android emülatöründe host makineye düz `http://10.0.2.2:8000` ile bağlanmak için `usesCleartextTraffic=true` içeren `--debug` derleme gerekir (release APK'da yalnızca `https://` izinlidir). Android 17+ (`targetSdk = 37`) yerel ağ IP'leri için `ACCESS_LOCAL_NETWORK` çalışma zamanı izni ister (`AndroidManifest.xml`'de tanımlıdır); emülatörde izinleri otomatik vermek için `adb install -r -g ...` kullanın:

```powershell
$env:NEXT_PUBLIC_API_URL = "http://10.0.2.2:8000"
node csp-config.mjs
cargo tauri android build --apk --debug --target x86_64 --config src-tauri/tauri.csp.json
& "$env:ANDROID_HOME\platform-tools\adb.exe" -s emulator-5554 install -r -g `
  src-tauri/gen/android/app/build/outputs/apk/universal/debug/app-universal-debug.apk
```

4. **API'ye ulaşılamadığında ne görünür?** Uygulama arayüzü normal açılır; üst çubuktaki son kontrol bilgisi boş/`-` kalır. Soru gönderildiğinde cevap alanında `"Sunucuya ulaşılamadı. Bağlantınızı kontrol edip tekrar deneyin."` hata mesajı gösterilir.

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
