"""Hugging Face Space'e yayın: API + statik arayüz tek kapsayıcıda (Docker Space, ücretsiz CPU).

Adımlar: arayüzü derle (aynı adresten sunulacak şekilde) -> yayın klasörünü kur (data/space_build, git dışı)
-> Space'i oluştur (yoksa) -> gizli değerleri ve değişkenleri ayarla -> dosyaları yükle. Space imajı kendisi derler.

Gizli değerler (.env'den okunur, HİÇBİR dosyaya/çıktıya yazılmaz; Space "secrets" olarak saklanır):
  GEMINI_API_KEY, QDRANT_URL (= QDRANT_CLOUD_URL), QDRANT_API_KEY (= QDRANT_CLOUD_API_KEY)

Kullanım: python -m scripts.yayin_space [--ad citelex] [--ozel] [--yukleme-yok]
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sqlite3
import subprocess
from pathlib import Path

from huggingface_hub import HfApi

from src import config  # noqa: F401  (.env yüklenir)

BUILD = Path("data/space_build")
MODEL_FILES = ["config.json", "pytorch_model.bin", "tokenizer.json", "tokenizer_config.json", "sentencepiece.bpe.model",
               "special_tokens_map.json", "colbert_linear.pt", "sparse_linear.pt", "modules.json",
               "config_sentence_transformers.json", "sentence_bert_config.json", "1_Pooling/*"]

DOCKERFILE = f'''# Citelex — Hugging Face Space (Docker). API + statik arayüz, port 7860, root olmayan kullanıcı (uid 1000).
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1 PYTHONIOENCODING=utf-8 \\
    HF_HOME=/app/.hf HF_HUB_DISABLE_TELEMETRY=1
WORKDIR /app
RUN pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install -r requirements.txt
# bge-m3: yalnız gereken dosyalar (~2,3 GB) imaja gömülür; depodaki onnx kopyası (~2 GB) indirilmez, soğuk açılış kısalır.
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download('BAAI/bge-m3', local_dir='/app/models/bge-m3', allow_patterns={MODEL_FILES!r})"
COPY src ./src
COPY configs ./configs
COPY web_out ./web_out
RUN useradd --create-home --uid 1000 user && mkdir -p /app/data /app/.hf && chown -R user /app/data /app/.hf
USER user
ENV CITELEX_BGE_PATH=/app/models/bge-m3 CITELEX_EMBED_DEVICE=cpu CITELEX_WEB_DIR=/app/web_out
EXPOSE 7860
CMD ["python", "-m", "uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "7860"]
'''

README = '''---
title: Citelex
emoji: ⚖️
colorFrom: red
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
short_description: Kaynak gösteren Türk mevzuatı asistanı (RAG)
---

# Citelex — kaynak gösteren mevzuat asistanı

KVKK, İş Kanunu, İSG Kanunu, ilgili yönetmelik/tebliğler ve seçilmiş KVKK Kurul kararları üzerine Türkçe soru-cevap.
Her cevap madde atfıyla gelir; kaynaklarda cevap yoksa sistem "bilmiyorum" der.

**Bu sistem hukuki tavsiye vermez.** Cevaplar yalnızca gösterilen kaynak metinlere dayanır.

Ücretsiz dil modeli kotası sınırlıdır; yoğun kullanımda "kota doldu" mesajı görülebilir.
'''

REQUIREMENTS = "FlagEmbedding==1.4.2\nqdrant-client==1.20.0\nhttpx==0.28.1\nnumpy==2.4.6\nfastapi==0.162.5\nuvicorn==0.54.0\n"


def son_kontrol() -> str:
    con = sqlite3.connect("data/store/citelex.db")
    try:
        return con.execute("SELECT MAX(finished) FROM runs WHERE finished IS NOT NULL AND n_error = 0").fetchone()[0] or ""
    finally:
        con.close()


def build_dir() -> None:
    npm = shutil.which("npm") or "npm"
    env = {**os.environ, "NEXT_PUBLIC_API_URL": "same-origin"}
    subprocess.run([npm, "--prefix", "web", "run", "build"], check=True, env=env, stdout=subprocess.DEVNULL)
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    shutil.copytree("src", BUILD / "src", ignore=ignore)
    shutil.copytree("configs", BUILD / "configs", ignore=ignore)
    shutil.copytree("web/out", BUILD / "web_out")
    (BUILD / "Dockerfile").write_text(DOCKERFILE, encoding="utf-8", newline="\n")
    (BUILD / "README.md").write_text(README, encoding="utf-8", newline="\n")
    (BUILD / "requirements.txt").write_text(REQUIREMENTS, encoding="utf-8", newline="\n")
    # Güvenlik ağı: yayın klasöründe gizli değer olmamalı
    gizli = [v for k in ("GEMINI_API_KEY", "QDRANT_CLOUD_API_KEY", "HF_TOKEN") if (v := os.environ.get(k))]
    for f in BUILD.rglob("*"):
        if f.is_file() and f.stat().st_size < 5_000_000:
            data = f.read_bytes()
            if f.name == ".env" or any(g.encode() in data for g in gizli):
                raise SystemExit(f"Gizli değer yayın klasöründe: {f}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ad", default="citelex")
    ap.add_argument("--ozel", action="store_true", help="Space'i özel (private) oluştur")
    ap.add_argument("--yukleme-yok", action="store_true", help="yalnız yayın klasörünü kur")
    args = ap.parse_args()
    build_dir()
    n = sum(1 for f in BUILD.rglob("*") if f.is_file())
    print(f"yayın klasörü hazır: {BUILD} ({n} dosya)")
    if args.yukleme_yok:
        return
    token, user = os.environ["HF_TOKEN"], os.environ["HF_USERNAME"]
    repo = f"{user}/{args.ad}"
    api = HfApi(token=token)
    api.create_repo(repo, repo_type="space", space_sdk="docker", private=args.ozel, exist_ok=True)
    qurl = re.sub(r"^(https?:/*)+", "https://", os.environ["QDRANT_CLOUD_URL"].strip())
    for k, v in {"GEMINI_API_KEY": os.environ["GEMINI_API_KEY"], "QDRANT_URL": qurl,
                 "QDRANT_API_KEY": os.environ["QDRANT_CLOUD_API_KEY"].strip()}.items():
        api.add_space_secret(repo, k, v)
    # GEMINI_MODEL: ücretsiz katmanda gemini-3.6-flash günde 20 istekle sınırlı (ölçüldü, 13 Kas); yayında ayrı kotası
    # olan lite model kullanılır. Bu modelin cevap kalitesi eval setinde ÖLÇÜLMEDİ (KARARLAR.md).
    for k, v in {"CITELEX_LLM": "gemini", "GEMINI_MODEL": os.environ.get("CITELEX_YAYIN_MODEL", "gemini-3.1-flash-lite"),
                 "CITELEX_TRUST_PROXY": "1", "CITELEX_RATE_DK": "5", "CITELEX_RATE_GUN": "60",
                 "CITELEX_GUNLUK_TOPLAM": os.environ.get("CITELEX_YAYIN_GUNLUK_TOPLAM", "300"),
                 "CITELEX_SON_KONTROL": son_kontrol()}.items():
        api.add_space_variable(repo, k, v)
    api.upload_folder(folder_path=str(BUILD), repo_id=repo, repo_type="space",
                      commit_message="Citelex yayını", delete_patterns=["*"])
    print(f"yüklendi: https://huggingface.co/spaces/{repo}  ->  https://{user.lower()}-{args.ad}.hf.space")


if __name__ == "__main__":
    main()
