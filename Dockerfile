# Citelex API (CPU). Model (bge-m3, ~2,3 GB) imaja gömülmez; ilk açılışta /models'e iner (compose'da kalıcı volume).
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1 \
    HF_HOME=/models PYTHONIOENCODING=utf-8
WORKDIR /app

# torch ayrı katman: CPU sürümü (GPU sürümü imajı ~5 GB büyütür, API sorgu başına tek embedding üretir)
RUN pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src ./src
COPY configs ./configs

# root olmayan kullanıcı; /models ve /app/data yazılabilir olmalı (model önbelleği, boş embedding önbelleği)
RUN useradd --create-home --uid 1000 citelex && mkdir -p /models /app/data && chown -R citelex /models /app
USER citelex

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=600s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/saglik', timeout=4).status == 200 else 1)"
CMD ["python", "-m", "uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
