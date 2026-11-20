"""kvkk.gov.tr ara sertifika göndermiyor: ek sertifika güven deposuna yüklenmeli, doğrulama açık kalmalı."""
import ssl

import certifi

from src.sources.http import EK_SERTIFIKALAR, ssl_baglami


def test_ek_ara_sertifika_yukleniyor():
    assert EK_SERTIFIKALAR.exists()
    temel = ssl.create_default_context(cafile=certifi.where()).cert_store_stats()["x509_ca"]
    ctx = ssl_baglami()
    assert ctx.cert_store_stats()["x509_ca"] == temel + 1
    assert ctx.verify_mode == ssl.CERT_REQUIRED and ctx.check_hostname
