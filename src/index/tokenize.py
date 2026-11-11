"""BM25 için Türkçe tokenizasyon.

Adımlar: NFC -> Türkçe küçük harf (I->ı, İ->i; str.lower() bunu yanlış yapar) -> harf/rakam
dizilerine bölme -> stopword atma -> ilk 5 karakter kesimi (F5 kök bulma).

F5: Türkçe eklemeli bir dil; "işçinin", "işçiye", "işçiler" -> "işçi*". Önek kesimi Türkçe bilgi
erişiminde morfolojik çözümleyicilere yakın sonuç veriyor (Can vd., 2008) ve bağımlılık gerektirmiyor.
Sayılar kesilmez ("6698", "4857" tam eşleşmeli).

TOKENIZER_VERSION değişirse BM25 indeksi tam yeniden kurulmalıdır.
"""
from __future__ import annotations

import re
import unicodedata

TOKENIZER_VERSION = "tr-f5-v1"
PREFIX = 5

_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)

# Kısa liste: bağlaç, edat, zamir. Hukuki anlamı olan "değil", "hariç", "ancak" vb. tutulur.
STOPWORDS = frozenset(
    """
    ve veya ile ya da de ki bu şu o bir her için gibi olan olarak ise ilgili
    göre kadar daha en çok az mi mı mu mü ne nasıl hangi kim ben sen biz siz onlar
    bunlar şunlar bunun şunun onun bu ise ayrıca hem
    """.split()
)


def turkish_lower(text: str) -> str:
    return unicodedata.normalize("NFC", text).replace("I", "ı").replace("İ", "i").lower()


def tokenize(text: str) -> list[str]:
    out = []
    for tok in _TOKEN_RE.findall(turkish_lower(text)):
        if tok in STOPWORDS:
            continue
        if not tok.isdigit():
            tok = tok[:PREFIX]
        out.append(tok)
    return out
