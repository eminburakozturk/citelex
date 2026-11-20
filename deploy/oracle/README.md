# Oracle Cloud Always Free ile yayın

Tek sanal makinede Qdrant + API + Caddy (otomatik HTTPS). Yayın yapılandırması: ajan açık, reranker kapalı
(CPU'da ~43 sn/sorgu), geniş katman açık. Gizli değerler yalnız sunucudaki `.env`'de.

## 1. Hesap ve sanal makine (senin adımın; kart doğrulaması Oracle'ın kendi sayfasında)
1. cloud.oracle.com'da Free Tier hesabı aç (ev bölgesi sonradan değişmez; Ampere A1 kapasitesi olan bir bölge seç).
2. Compute → Instances → Create:
   - Image: **Canonical Ubuntu 24.04** (veya 22.04)
   - Shape: **VM.Standard.A1.Flex** (Ampere ARM), **4 OCPU, 24 GB RAM** (Always Free sınırı içinde)
   - Boot volume: 100 GB yeterli (Always Free toplam 200 GB)
   - SSH anahtarı: kendi açık anahtarını yükle (ya da Oracle'ın ürettiğini indir).
   "Out of capacity" hatası alırsan (Frankfurt'ta üç AD de doluydu): OCI API anahtarı oluştur (`~/.oci/config`) ve
   `python deploy/oracle/a1_dene.py --subnet <ocid> --image <ocid> --ssh ~/.ssh/id_ed25519.pub` ile kapasite açılana
   kadar otomatik dene.
3. Networking → VCN → Security List → Ingress Rules: **TCP 80** ve **TCP 443**, kaynak `0.0.0.0/0` ekle.
4. Makinenin **genel IP**'sini not et. Alan adın yoksa adres: `<ip-tireli>.sslip.io`
   (ör. IP 129.146.10.20 -> `129-146-10-20.sslip.io`); sertifikayı Caddy kendisi alır.

## 2. Paketi hazırla (kendi bilgisayarında, Qdrant çalışırken)
```bash
C:\Users\Burak\anaconda3\envs\citelex\python.exe -m scripts.yayin_oracle
scp deploy/citelex_paket.tar.gz ubuntu@<IP>:~
```
Paket: commit'lenmiş kod + Qdrant anlık görüntüleri (derin + geniş katman) + statik arayüz + sürüm deposu.
`.env` pakete girmez; paket gizli değer kalıbı içeriyorsa betik durur.

## 3. Sunucuda kur
```bash
ssh ubuntu@<IP>
sudo tar xzf citelex_paket.tar.gz   # sudo: kapsayıcı verisi uid 1000'e aittir
bash citelex/deploy/oracle/kurulum.sh <ip-tireli>.sslip.io
```
Betik Docker'ı kurar, 80/443'ü iptables'ta açar, OpenRouter anahtarını sorar (`.env`, yalnız sahibi okur), indeksi
geri yükler, API'yi derler (ARM'de ilk derleme ~10-15 dk; bge-m3 ilk açılışta ~2,3 GB iner) ve sağlık kontrolü yapar.

## 4. Kontrol
- Duman testi (kendi bilgisayarından):
  ```bash
  C:\Users\Burak\anaconda3\envs\citelex\python.exe scripts/duman_testi.py https://<adres>
  ```
- `https://<adres>/saglik` -> `"durum": "ok"`
- `https://<adres>/` -> arayüz; bir soru sor.
- Günlükler: `sudo docker compose -f citelex/deploy/oracle/docker-compose.oracle.yml logs -f api`

## Güncelleme
Yeni sürüm: paketi yeniden üret, kopyala, `sudo tar xzf` (üzerine yazar; `.env` korunur), `kurulum.sh` yeniden çalıştır.
**Günlük otomatik güncelleme sunucuda kuruludur** (kurulum.sh cron'a ekler; her gün 03:00):
kaynakları (mevzuat.gov.tr, kvkk.gov.tr) kontrol eder, değişen belgeyi yeniden ayrıştırır, Qdrant'ı artımlı günceller
(yalnız değişen parçalar embed edilir), madde farkını üretir (/degisiklikler), Resmî Gazete erken uyarısını yazar ve
arama regresyonunu çalıştırır. Günlük: `citelex/logs/guncelle.log`; özet: `citelex/logs/updates.jsonl`.
Elle çalıştırma: `sudo docker compose --env-file .env -f deploy/oracle/docker-compose.oracle.yml --profile guncelle run --rm guncelle`
Geniş katman (~900 kanun) otomatik güncellenmez.

## Bilinen sınırlar
- Tek makine, yedeklilik yok. İstek sınırı: IP başına 5/dk, 60/gün; günlük toplam tavan 300 (`CITELEX_GUNLUK_TOPLAM`).
- LLM zinciri: önce ücretsiz model; kota dolunca yedek modeller (KARARLAR.md).
