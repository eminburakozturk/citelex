import os

os.environ["CITELEX_IZ_DOSYA"] = "0"   # testler logs/izler.jsonl'e iz yazmasın
os.environ.pop("OTEL_EXPORTER_OTLP_ENDPOINT", None)
