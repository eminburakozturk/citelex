# Günlük güncelleme (Windows Görev Zamanlayıcı bunu çalıştırır).
# Qdrant kapalıysa Docker Desktop'ı ve konteyneri başlatır, ardından src.update.run'ı çalıştırır.
# Çıktı logs/scheduler.log'a eklenir; özet ayrıca logs/updates.jsonl ve data/store/citelex.db'de.
$ErrorActionPreference = "Continue"
$proje = Split-Path -Parent $PSScriptRoot
Set-Location $proje
$py = "C:\Users\Burak\anaconda3\envs\citelex\python.exe"
$log = Join-Path $proje "logs\scheduler.log"
New-Item -ItemType Directory -Force (Join-Path $proje "logs") | Out-Null
"==== $(Get-Date -Format s) başlıyor" | Out-File -Append -Encoding utf8 $log

try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 http://127.0.0.1:6333/collections | Out-Null }
catch {
    "Qdrant kapalı; Docker başlatılıyor" | Out-File -Append -Encoding utf8 $log
    docker version 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        foreach ($i in 1..36) { Start-Sleep 5; docker version 2>$null | Out-Null; if ($LASTEXITCODE -eq 0) { break } }
    }
    docker start citelex-qdrant | Out-Null
    Start-Sleep 5
}

$env:PYTHONIOENCODING = "utf-8"
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = "1"
& $py -m src.update.run *>&1 | Out-File -Append -Encoding utf8 $log
"==== $(Get-Date -Format s) çıkış kodu $LASTEXITCODE" | Out-File -Append -Encoding utf8 $log
exit $LASTEXITCODE
