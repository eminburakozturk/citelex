"""Hakem: JSON ayrıştırma, uyarı cümlelerinin sayılmaması, [n] -> bağlam anahtarı eşlemesi (sahte LLM)."""
from __future__ import annotations

import json

from eval.judge import judge_one


class FakeLLM:
    name, last_model, last_usage = "sahte", None, None

    def __init__(self, out: dict):
        self.out, self.user = json.dumps(out, ensure_ascii=False), None

    def generate(self, system, user, max_tokens=1500):
        self.user = user
        return "```json\n" + self.out + "\n```"


ROW = {"soru": "Yazılı mı?", "cevap": "Bir yıl ve üzeri yazılıdır [2]. Bu karar olaya özgüdür.",
       "baglam_anahtar": ["a:1", "is-kanunu:8"]}


def test_uyari_sayilmaz_ve_kaynak_eslesir():
    llm = FakeLLM({"iddialar": [
        {"iddia": "Bir yıl ve üzeri yazılıdır", "atif": [2], "etiket": "destekli", "gerekce": "-"},
        {"iddia": "Bu karar olaya özgüdür.", "atif": [], "etiket": "uyari", "gerekce": "-"}]})
    h = judge_one(llm, ROW, {"is-kanunu:8": "MADDE 8 METNİ", "a:1": "İLGİSİZ"})
    assert h["sadik"] and h["n_iddia"] == 1 and h["uyari"] == 1 and h["destekli"] == 1
    assert "[2] MADDE 8 METNİ" in llm.user and "İLGİSİZ" not in llm.user   # yalnız atıf yapılan kaynak gider


def test_desteksiz_iddia_sadakati_bozar():
    llm = FakeLLM({"iddialar": [{"iddia": "x", "atif": [2], "etiket": "desteksiz", "gerekce": "yok"}]})
    h = judge_one(llm, ROW, {"is-kanunu:8": "M"})
    assert not h["sadik"] and h["desteksiz"] == 1


def test_gecersiz_etiket_hata():
    llm = FakeLLM({"iddialar": [{"iddia": "x", "atif": [], "etiket": "belki"}]})
    assert "hata" in judge_one(llm, ROW, {})
