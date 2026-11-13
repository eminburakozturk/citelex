# Arama karşılaştırma deneyleri

Sorular: 63 (beklenen kaynağı olanlar: eval/questions.jsonl + eval/retrieval_smoke.jsonl). Küçük örneklem: 1-2 soruluk farklar gürültüdür. Reranker kapalı (ayrı ölçüm: results/rerank_compare.md).

## 1. Parçalama × yöntem (Qdrant, iki kanal)

| Parçalama | Yöntem | Mevzuat R@1 | Mevzuat R@5 | Mevzuat MRR | Karar R@1 | Karar R@3 | Süre (sn/soru) |
|---|---|---|---|---|---|---|---|
| madde | dense | 45/51 | 50/51 | 0.931 | 12/12 | 12/12 | 0.56 |
| madde | bm25 | 40/51 | 48/51 | 0.848 | 11/12 | 12/12 | 0.05 |
| madde | hybrid | 44/51 | 48/51 | 0.902 | 11/12 | 12/12 | 0.06 |
| fikra | dense | 47/51 | 50/51 | 0.951 | 12/12 | 12/12 | 0.17 |
| fikra | bm25 | 40/51 | 48/51 | 0.848 | 11/12 | 12/12 | 0.10 |
| fikra | hybrid | 44/51 | 48/51 | 0.902 | 11/12 | 12/12 | 0.11 |
| hibrit | dense | 45/51 | 50/51 | 0.931 | 12/12 | 12/12 | 0.13 |
| hibrit | bm25 | 41/51 | 48/51 | 0.858 | 11/12 | 12/12 | 0.09 |
| hibrit | hybrid | 43/51 | 48/51 | 0.892 | 11/12 | 12/12 | 0.09 |

## 2. Sözcüksel kanal: BM25 vs bge-m3 sparse (bellekte, hibrit parçalar, mevzuat kanalı)

607 aktif mevzuat parçası; bge-m3 sparse kodlama 3 sn (GPU fp16).

| Yöntem | R@1 | R@5 | MRR@5 |
|---|---|---|---|
| BM25 (Türkçe tokenizer) | 38/51 | 48/51 | 0.837 |
| bge-m3 sparse | 45/51 | 47/51 | 0.902 |
