"""İstemci tarafı RRF: formül ve deterministik eşitlik kırma (Qdrant'ın RrfQuery'si eşitlikleri rastgele sıralıyordu)."""
from src.retrieve.search import rrf_birlestir


class P:
    def __init__(self, i):
        self.id, self.payload = i, {"chunk_id": f"c{i}"}


def test_rrf_esitlik_dense_sirasiyla_kirilir():
    # a: dense 1 + sparse 3; b: dense 3 + sparse 1 -> eşit puan; dense'te önde olan (a) önce gelir
    a, b, c = P(1), P(2), P(3)
    out = rrf_birlestir([a, c, b], [b, c, a], top_k=3, k=60)
    # a,b: 1/61 + 1/63 (eşit) > c: 2/62  -> sıra a, b, c
    assert [h.payload["chunk_id"] for h in out] == ["c1", "c2", "c3"]
    # tekrarlanabilirlik
    assert [h.payload["chunk_id"] for h in out] == [h.payload["chunk_id"] for h in rrf_birlestir([a, c, b], [b, c, a], 3, 60)]


def test_rrf_formulu():
    a, b = P(1), P(2)
    out = rrf_birlestir([a, b], [a], top_k=2, k=60)
    assert out[0].payload["chunk_id"] == "c1" and abs(out[0].score - (1 / 61 + 1 / 61)) < 1e-12
    assert abs(out[1].score - 1 / 62) < 1e-12
