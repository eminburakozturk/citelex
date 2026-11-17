#!/usr/bin/env bash
# Citelex — Oracle Cloud (Ubuntu 22.04/24.04, ARM Ampere A1) kurulum betiği. Sunucuda, paket ev dizinindeyken:
#   tar xzf citelex_paket.tar.gz && bash citelex/deploy/oracle/kurulum.sh <ALAN_ADI>
# ALAN_ADI yoksa: <genel-ip-tireli>.sslip.io (ör. 129-146-10-20.sslip.io). Betik yeniden çalıştırılabilir.
set -euo pipefail
ALAN_ADI="${1:?kullanım: kurulum.sh <alan-adı veya ip-tireli.sslip.io>}"
cd "$(dirname "$0")/../.."          # citelex/ kökü
KOK="$(pwd)"

echo "== 1/6 Docker"
if ! command -v docker >/dev/null; then
  sudo apt-get update -y && sudo apt-get install -y ca-certificates curl
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER"
fi
DOCKER="sudo docker"

echo "== 2/6 Güvenlik duvarı (Oracle Ubuntu imajı iptables ile 80/443'ü kapatır)"
for p in 80 443; do
  sudo iptables -C INPUT -p tcp --dport "$p" -j ACCEPT 2>/dev/null || sudo iptables -I INPUT 6 -p tcp --dport "$p" -j ACCEPT
done
sudo apt-get install -y iptables-persistent >/dev/null 2>&1 || true
sudo netfilter-persistent save || true

echo "== 3/6 .env (gizli değerler)"
if [ ! -f .env ]; then
  read -rsp "OPENROUTER_API_KEY: " KEY; echo
  read -rp  "OPENROUTER_MODELS (virgüllü; boş = önerilen zincir): " MODELS
  MODELS="${MODELS:-nvidia/nemotron-3-ultra-550b-a55b:free,deepseek/deepseek-v4.1-flash-1017,qwen/qwen3.7-flash}"
  umask 077
  printf 'CITELEX_LLM=openrouter\nOPENROUTER_API_KEY=%s\nOPENROUTER_MODELS=%s\nALAN_ADI=%s\n' "$KEY" "$MODELS" "$ALAN_ADI" > .env
else
  grep -q '^ALAN_ADI=' .env || echo "ALAN_ADI=$ALAN_ADI" >> .env
fi
mkdir -p logs store veri/results
export ALAN_ADI

COMPOSE="$DOCKER compose --env-file .env -f deploy/oracle/docker-compose.oracle.yml"
echo "== 4/6 Qdrant + indeks geri yükleme"
$COMPOSE up -d qdrant
# Qdrant imajında curl olmayabilir: istekler aynı ağdaki geçici bir curl kapsayıcısından gönderilir.
CURL="$DOCKER run --rm --network citelex_default curlimages/curl:8.11.1 -sf"
for i in $(seq 1 30); do $CURL http://qdrant:6333/readyz >/dev/null 2>&1 && break; sleep 2; done
QID="$($COMPOSE ps -q qdrant)"
for s in snapshots/*.snapshot; do
  name="$(basename "$s" .snapshot)"
  $DOCKER exec "$QID" mkdir -p /qdrant/snapshots   # Qdrant yalnız bu klasörden geri yükler
  $DOCKER cp "$s" "$QID:/qdrant/snapshots/$name.snapshot"
  $CURL -X PUT "http://qdrant:6333/collections/$name/snapshots/recover?wait=true" -H 'Content-Type: application/json'     -d "{\"location\":\"file:///qdrant/snapshots/$name.snapshot\",\"priority\":\"snapshot\"}" >/dev/null
  $DOCKER exec "$QID" rm -f "/qdrant/snapshots/$name.snapshot"
  echo "  $name: $($CURL http://qdrant:6333/collections/$name | grep -o '"points_count":[0-9]*')"
done

echo "== 5/6 API + Caddy (ilk derleme ARM'de ~10-15 dk; bge-m3 ilk açılışta iner)"
$COMPOSE up -d --build api caddy

echo "== Günlük güncelleme (cron, her gün 03:00; günlük: logs/guncelle.log)"
mkdir -p veri/results
CRON="0 3 * * * cd $KOK && $COMPOSE --profile guncelle run --rm guncelle >> $KOK/logs/guncelle.log 2>&1"
( crontab -l 2>/dev/null | grep -v 'run --rm guncelle' ; echo "$CRON" ) | crontab -
# Sudo gerektiren docker komutu cron'da çalışsın diye kullanıcı docker grubundaysa sudo'suz sürüm kullanılır.
if id -nG "$USER" | grep -qw docker; then crontab -l | sed 's/sudo docker/docker/' | crontab -; fi

echo "== 6/6 Sağlık kontrolü (en çok 20 dk)"
for i in $(seq 1 120); do
  if $COMPOSE exec -T api python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/saglik',timeout=4)" 2>/dev/null; then
    echo "HAZIR: https://$ALAN_ADI"; exit 0
  fi
  sleep 10
done
echo "API 20 dk içinde hazır olmadı: $COMPOSE logs api --tail 50"; exit 1
