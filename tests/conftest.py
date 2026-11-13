import os

os.environ["CITELEX_IZ_DOSYA"] = "0"   # testler logs/izler.jsonl'e iz yazmasın
os.environ.pop("OTEL_EXPORTER_OTLP_ENDPOINT", None)
os.environ["CITELEX_AJAN"] = "0"       # mevcut testler tek adımlı yolu sınar; ajan testi ajan=True gönderir
