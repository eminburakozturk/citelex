# Reranker ölçümü (BAAI/bge-reranker-v2-m3, hibrit ilk 30 aday)

Sorular: eval/questions.jsonl + eval/retrieval_smoke.jsonl (beklenen kaynağı olanlar). Sıra madde/karar düzeyinde (aynı maddenin parçaları tek sayılır). MRR ilk 10'a göre.

| Kanal | Yöntem | n | R@1 | R@3 | R@5 | MRR |
|---|---|---|---|---|---|---|
| mevzuat | hibrit | 51 | 43 | 48 | 48 | 0.898 |
| mevzuat | hibrit + reranker | 51 | 48 | 49 | 50 | 0.957 |
| karar | hibrit | 12 | 11 | 12 | 12 | 0.958 |
| karar | hibrit + reranker | 12 | 12 | 12 | 12 | 1.0 |

Rerank süresi: medyan 0.74 sn/sorgu (30 aday, GPU fp16).

## Sırası değişen sorular

| # | Kanal | Önce | Sonra |
|---|---|---|---|
| e02 | mevzuat | 6 | 5 |
| e03 | mevzuat | 2 | 1 |
| e13 | mevzuat | 17 | 8 |
| e27 | mevzuat | 7 | 2 |
| e30 | mevzuat | 2 | 1 |
| e35 | mevzuat | 2 | 1 |
| e39 | karar | 2 | 1 |
| r08 | mevzuat | 2 | 1 |
| r09 | mevzuat | 2 | 1 |
