"""Prompt ve cevap biçimi.

Tasarım:
  - Model yalnızca numaralı kaynaklardan cevap verir; her iddia [n] ile kaynağa bağlanır.
  - Kaynaklar cevabı içermiyorsa model ilk satıra tam olarak CEVAP_YOK yazar (makinece ayrıştırılabilir "bilmiyorum").
  - Atıf metnini (ör. "6698 s. KVKK m. 5/2") model YAZMAZ; [n] numarasından kod üretir. Böylece
    uydurma madde numarası cevaba giremez: var olmayan [n] doğrulamada yakalanır.
"""
from __future__ import annotations

import re

NO_ANSWER = "CEVAP_YOK"
NO_ANSWER_TEXT = "Bu soruya elimdeki kaynaklarla cevap veremiyorum."

SYSTEM = f"""Sen Türk mevzuatı üzerine çalışan bir kaynak gösterme asistanısın. Görevin, sana verilen KAYNAKLAR'a dayanarak soruyu Türkçe cevaplamak.

Kurallar:
1. YALNIZCA aşağıdaki KAYNAKLAR'da yazan bilgiyi kullan. Kendi bilgini, tahminini veya kaynaklarda olmayan sayı/süre/oranları ekleme.
2. Her cümlenin sonuna dayandığı kaynağın numarasını köşeli parantezle yaz: [1] veya [2][5]. Kaynak göstermeden iddiada bulunma.
   KAYNAKLAR'ın bir kısmı soruyla ilgisiz olabilir; ilgisiz kaynakları yok say ve numaralarını yazma. Bir kaynağın numarasını yalnızca o kaynakta gerçekten yazan bilgi için kullan. "Mevzuatta bu konuda hüküm yoktur" gibi olumsuz genellemeler yapma; sana verilen kaynaklar mevzuatın tamamı değildir.
3. Kaynaklar soruyu cevaplamaya yetmiyorsa ilk satıra yalnızca {NO_ANSWER} yaz, ikinci satırda neyin eksik olduğunu bir cümleyle söyle. Konu yakın diye cevap uydurma.
4. Kaynaklar sorunun yalnızca bir kısmını cevaplıyorsa o kısmı cevapla ve neyin kaynaklarda bulunmadığını açıkça belirt.
5. Kanun/yönetmelik hükmü ile Kurul kararını ayırt et: genel kuralı mevzuattan ver; Kurul kararını "şu olayda Kurul şöyle karar vermiştir" diye, somut olaya özgü olduğunu belirterek aktar. Bir Kurul kararındaki sonucu her duruma uygulanan genel kural gibi sunma.
   Kurul kararı kaynaklarında ROL satırına bak: yalnızca "Kurulun değerlendirmesi" ve "Kurulun kararı / hüküm" Kurulun görüşüdür. Şikâyet ve savunma bölümleri tarafların iddiasıdır; bunları kural veya Kurul görüşü gibi aktarma.
6. Kısa ve net yaz (en çok 6-7 cümle). Madde numarasını kendin yazma; yalnızca [n] kullan. Hukuki tavsiye verme, kişiye özel yönlendirme yapma."""


# Karar bölümünün rolü kaynağın başına yazılır: taraf beyanı ile Kurulun görüşü karışmasın.
KARAR_ROL = {
    "sikayet": "\n(ROL: ilgili kişinin iddiası / bildirim — Kurulun görüşü DEĞİLDİR)",
    "savunma": "\n(ROL: veri sorumlusunun savunması — Kurulun görüşü DEĞİLDİR)",
    "degerlendirme": "\n(ROL: Kurulun değerlendirmesi)",
    "hukum": "\n(ROL: Kurulun kararı / hüküm)",
}


def format_sources(hits: list) -> str:
    out = []
    for i, h in enumerate(hits, 1):
        p = h.payload
        tur = {"kanun": "Kanun", "yonetmelik": "Yönetmelik", "teblig": "Tebliğ", "karar": "Kurul kararı"}[p["belge_tur"]]
        baslik = f" — {p['baslik']}" if p.get("baslik") else ""
        rol = KARAR_ROL.get(p.get("bolum"), "") if p["belge_tur"] == "karar" else ""
        out.append(f"[{i}] ({tur}) {p['atif']}{baslik}{rol}\n{p['metin']}")
    return "\n\n".join(out)


def build_user(query: str, hits: list) -> str:
    return f"KAYNAKLAR:\n\n{format_sources(hits)}\n\nSORU: {query}\n\nCEVAP:"


_CITE = re.compile(r"\[(\d{1,2})\]")


def parse_answer(text: str, n_sources: int) -> dict:
    """LLM çıktısı -> {bilmiyorum, cevap, atif_no (geçerli), gecersiz_atif}."""
    t = text.strip()
    if t.upper().startswith(NO_ANSWER):
        neden = t[len(NO_ANSWER):].strip(" \n:-")
        return {"bilmiyorum": True, "cevap": NO_ANSWER_TEXT, "neden": neden, "atif_no": [], "gecersiz_atif": []}
    nums = [int(x) for x in _CITE.findall(t)]
    ok = sorted({n for n in nums if 1 <= n <= n_sources})
    bad = sorted({n for n in nums if not 1 <= n <= n_sources})
    return {"bilmiyorum": False, "cevap": t, "neden": "", "atif_no": ok, "gecersiz_atif": bad}
