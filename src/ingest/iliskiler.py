"""Derin katman maddeleri için değişiklik geçmişi ve madde-madde ilişki grafi çıkarır."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ARTICLES_PATH = Path("data/processed/articles.jsonl")
SOURCES_PATH = Path("configs/sources.json")
OUT_PATH = Path("data/processed/iliskiler.json")

# Madde metni içinde kalmış parantez içi değişiklik şerhlerini ve tırnak içi alıntıları temizlemek için
RE_INLINE_ANNOT = re.compile(
    r"\(\s*(?:Değişik|Ek|Mülga|İptal|Yeniden\s+düzenleme)\b[^)]{0,220}?\)",
    re.IGNORECASE,
)
RE_QUOTED_SPAN = re.compile(r"[“\"][^”\"]*[”\"]")

# Değişiklik notunu ";" üzerinden alt olaylara ayırırken yalnızca yeni bir işlem etiketiyle başlayanları böl
RE_NOTE_SPLIT = re.compile(
    r";\s*(?=(?:Değişik|Ek|Mülga|İptal|Yeniden)\b[^:]{0,60}:)",
    re.IGNORECASE,
)

RE_AYM = re.compile(
    r"Anayasa\s+Mahkemesi(?:nin|’nin|'nin)?\s+"
    r"(?P<g>\d{1,2})/(?P<a>\d{1,2})/(?P<y>\d{4})\s+tarihli\s+ve\s+"
    r"E\.?\s*:?\s*(?P<esas>\d+/\d+)\s*[,;]\s*K\.?\s*:?\s*(?P<karar>\d+/\d+)",
    re.IGNORECASE,
)
RE_RG_NOTE = re.compile(
    r"RG\s*[-–:]\s*(?P<g>\d{1,2})/(?P<a>\d{1,2})/(?P<y>\d{4})\s*[-–]\s*(?P<rg>\d+)",
    re.IGNORECASE,
)
RE_KHK_NOTE = re.compile(
    r"(?P<g>\d{1,2})/(?P<a>\d{1,2})/(?P<y>\d{4})\s*[-–/]\s*KHK\s*[-–/]\s*(?P<no>\d+)\s*/\s*(?P<md>[\w/]+)\s*md\.?",
    re.IGNORECASE,
)
RE_KANUN_NOTE = re.compile(
    r"(?P<g>\d{1,2})/(?P<a>\d{1,2})/(?P<y>\d{4})\s*[-–/]\s*(?P<no>\d+)\s*/\s*(?P<md>[\w/]+)\s*md\.?",
    re.IGNORECASE,
)

RE_DIPNOT_KANUN = re.compile(
    r"(?P<g>\d{1,2})/(?P<a>\d{1,2})/(?P<y>\d{4})\s+tarih(?:li)?\s+ve\s+"
    r"(?P<no>\d+)\s+sayılı\s+"
    r"(?P<tur>Kanun\w*|Kanın\w*|KHK[’']?(?:nin|nın)?|Kanun\s+Hükmünde\s+Kararname\w*)"
    r"(?:n?[ıiuü]n|['’]n[ıiuü]n)?\s+(?P<md>[\w/]+)\s*(?:[ıiuü]nc[ıiuü]|nci|ncü|uncu|üncü)?\s+madde\w*",
    re.IGNORECASE,
)
RE_DIPNOT_KANUN_GENEL = re.compile(
    r"(?P<g>\d{1,2})/(?P<a>\d{1,2})/(?P<y>\d{4})\s+tarih(?:li)?\s+ve\s+"
    r"(?P<no>\d+)\s+sayılı\s+"
    r"(?P<tur>Kanun(?:la|\s+ile)|KHK[’']?\s*ile|Kanun\s+Hükmünde\s+Kararname(?:yle|\s+ile))\b",
    re.IGNORECASE,
)
RE_DIPNOT_CK = re.compile(
    r"(?P<g>\d{1,2})/(?P<a>\d{1,2})/(?P<y>\d{4})\s+tarih(?:li)?\s+ve\s+"
    r"(?P<rg>\d+)\s+sayılı\s+Resm[îi]\s+Gazete[’']?de\s+yayımlanan\s+"
    r"(?P<ck>\d+)\s+sayılı\s+Cumhurbaşkanı\s+Karar\w*",
    re.IGNORECASE,
)
RE_DIPNOT_RG = re.compile(
    r"(?P<g>\d{1,2})/(?P<a>\d{1,2})/(?P<y>\d{4})\s+tarih(?:li)?\s+ve\s+"
    r"(?P<rg>\d+)\s+sayılı\s+Resm[îi]\s+Gazete",
    re.IGNORECASE,
)

# Madde atıf yakalayıcı: isteğe bağlı belge ön eki + madde numara listesi/aralığı + "madde..."
_ITEM = r"(?:(?:ek|geçici)\s+)?\d+(?:/[A-ZÇĞİÖŞÜa-z])?"
_ORD = r"(?:\s*(?:[’']?\s*)?(?:inci|ıncı|üncü|uncu|nci|ncı|ncü|ncu))?"
_ITEM_LIST = (
    rf"(?:{_ITEM}{_ORD}"
    rf"(?:\s*(?:,\s*{_ITEM}{_ORD})*"
    rf"(?:\s*(?:ve|ile|ila|veya)\s*{_ITEM}{_ORD})+)?)"
)
RE_MADDE_REF = re.compile(
    rf"(?P<prefix>[^.;:\n()]{{0,140}}?)"
    rf"(?P<items>{_ITEM_LIST})"
    rf"\s+madde(?:s[iı]\w*|l[ea]r\w*|y[ea]|d[ea]n?|n[iı]n)?\b",
    re.IGNORECASE | re.UNICODE,
)

RE_HARICI_KANUN_NO = re.compile(r"\b(\d{3,5})\s+sayılı\b", re.IGNORECASE)
# Özel adlı mevzuat: baş harfi büyük kelimeler (arada yalnızca kısa bağlaçlar) + Kanun/Yönetmelik/Tebliğ/Kararname
RE_HARICI_BELGE_ADI = re.compile(
    r"\b(?:[A-ZÇĞİÖŞÜ][A-Za-zÇĞİÖŞÜçğıöşü’']+\s+(?:(?:ve|ile|veya|hakkında|dair|ilişkin)\s+)?){1,6}"
    r"(?:Kanun\w*|Kararname\w*|Yönetmeli[ğg]\w*|Tebli[ğg]\w*|Tüzü[ğg]\w*)",
    re.UNICODE,
)

DERIN_KANUN_NO_MAP = {
    "6698": "kvkk",
    "4857": "is-kanunu",
    "1475": "is-kanunu-1475",
    "6331": "isg-kanunu",
}


def _iso_date(g: str, a: str, y: str) -> str | None:
    gun, ay, yil = int(g), int(a), int(y)
    if not (1 <= ay <= 12 and 1 <= gun <= 31 and 1900 <= yil <= 2100):
        return None
    return f"{yil:04d}-{ay:02d}-{gun:02d}"


def _dipnot_aciklama(metin: str) -> str:
    low = metin.lower()
    if "iptal edilmiş" in low or "iptal edilmiştir" in low:
        return "İptal (dipnot)"
    if "yürürlükten kaldırılmış" in low or "çıkarılmıştır" in low or "çıkartılmıştır" in low:
        return "Yürürlükten kaldırma"
    if "başlığı" in low and "değiştiril" in low:
        return "Başlık değişikliği"
    if "eklenmiştir" in low or "eklenmiş" in low:
        return "İbare/hüküm eklenmesi"
    if "değiştirilmiştir" in low or "değiştirilmiş" in low:
        return "İbare/hüküm değişikliği"
    if "uzatılmasına karar" in low:
        return "Süre uzatımı"
    if "bakınız" in low:
        return "Resmî Gazete atfı"
    return "Değişiklik (dipnot)"


def parse_degisiklik_notu(not_metni: str) -> tuple[list[dict], int]:
    """Tek bir degisiklik_notlari dizgesinden tarihli kayıtları ve tarihsiz sayısını döndürür."""
    s = not_metni.strip()
    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1].strip()
    if not s:
        return [], 0

    kayitlar: list[dict] = []
    tarihsiz = 0
    for parca in RE_NOTE_SPLIT.split(s):
        parca = parca.strip()
        if not parca:
            continue
        if ":" in parca and not re.match(r"^[A-ZÇĞİÖŞÜ]+\s*:", parca):
            aciklama_ham, _, govde = parca.partition(":")
            aciklama = re.sub(r"\s+", " ", aciklama_ham).strip()
        elif parca.lower().startswith(("değişik", "ek", "mülga", "iptal", "yeniden")):
            aciklama_ham, _, govde = parca.partition(":")
            aciklama = re.sub(r"\s+", " ", aciklama_ham).strip()
        else:
            aciklama, govde = "Değişiklik", parca

        if m := RE_AYM.search(parca):
            tarih = _iso_date(m.group("g"), m.group("a"), m.group("y"))
            if tarih:
                kayitlar.append({
                    "tarih": tarih,
                    "kanun": f"AYM E.{m.group('esas')}, K.{m.group('karar')}",
                    "aciklama": aciklama,
                })
                continue
        if m := RE_RG_NOTE.search(parca):
            tarih = _iso_date(m.group("g"), m.group("a"), m.group("y"))
            if tarih:
                kayitlar.append({
                    "tarih": tarih,
                    "kanun": f"RG {m.group('rg')}",
                    "aciklama": aciklama,
                })
                continue
        if m := RE_KHK_NOTE.search(govde or parca):
            tarih = _iso_date(m.group("g"), m.group("a"), m.group("y"))
            if tarih:
                kayitlar.append({
                    "tarih": tarih,
                    "kanun": f"{m.group('no')} s. KHK md. {m.group('md')}",
                    "aciklama": aciklama,
                })
                continue
        if m := RE_KANUN_NOTE.search(govde or parca):
            tarih = _iso_date(m.group("g"), m.group("a"), m.group("y"))
            if tarih:
                kayitlar.append({
                    "tarih": tarih,
                    "kanun": f"{m.group('no')} s. Kanun md. {m.group('md')}",
                    "aciklama": aciklama,
                })
                continue

        tarihsiz += 1

    return kayitlar, tarihsiz


def parse_dipnot(metin: str) -> tuple[list[dict], int]:
    """Tek bir dipnot metninden tarihli değişiklik kayıtlarını çıkarır."""
    s = re.sub(r"\s+", " ", metin).strip()
    if not s:
        return [], 0

    kayitlar: list[dict] = []
    # Birden fazla cümle içeren dipnotlarda (ör. Geçici 10) her cümleyi ayrı incele
    sentences = [c.strip() for c in re.split(r"(?<=\.)\s+", s) if c.strip()]
    had_match = False

    for cumle in sentences:
        matched_here = False
        for m in RE_DIPNOT_KANUN.finditer(cumle):
            tarih = _iso_date(m.group("g"), m.group("a"), m.group("y"))
            if not tarih:
                continue
            tur = "KHK" if ("khk" in m.group("tur").lower() or "kararname" in m.group("tur").lower()) else "Kanun"
            kayitlar.append({
                "tarih": tarih,
                "kanun": f"{m.group('no')} s. {tur} md. {m.group('md')}",
                "aciklama": _dipnot_aciklama(cumle),
            })
            matched_here = True
            had_match = True

        if not matched_here:
            for m in RE_DIPNOT_KANUN_GENEL.finditer(cumle):
                tarih = _iso_date(m.group("g"), m.group("a"), m.group("y"))
                if not tarih:
                    continue
                tur = "KHK" if ("khk" in m.group("tur").lower() or "kararname" in m.group("tur").lower()) else "Kanun"
                kayitlar.append({
                    "tarih": tarih,
                    "kanun": f"{m.group('no')} s. {tur}",
                    "aciklama": _dipnot_aciklama(cumle),
                })
                matched_here = True
                had_match = True

        if not matched_here and (m := RE_AYM.search(cumle)):
            tarih = _iso_date(m.group("g"), m.group("a"), m.group("y"))
            if tarih:
                kayitlar.append({
                    "tarih": tarih,
                    "kanun": f"AYM E.{m.group('esas')}, K.{m.group('karar')}",
                    "aciklama": _dipnot_aciklama(cumle),
                })
                matched_here = True
                had_match = True

        if not matched_here and (m := RE_DIPNOT_CK.search(cumle)):
            tarih = _iso_date(m.group("g"), m.group("a"), m.group("y"))
            if tarih:
                kayitlar.append({
                    "tarih": tarih,
                    "kanun": f"{m.group('ck')} s. CK (RG {m.group('rg')})",
                    "aciklama": _dipnot_aciklama(cumle),
                })
                matched_here = True
                had_match = True

        if not matched_here and (m := RE_DIPNOT_RG.search(cumle)):
            tarih = _iso_date(m.group("g"), m.group("a"), m.group("y"))
            if tarih:
                kayitlar.append({
                    "tarih": tarih,
                    "kanun": f"RG {m.group('rg')}",
                    "aciklama": _dipnot_aciklama(cumle),
                })
                had_match = True

    return kayitlar, (0 if had_match else 1)


def extract_gecmis(article: dict) -> tuple[list[dict], int]:
    """Maddenin degisiklik_notlari ve dipnotlar alanlarından sıralı geçmiş listesi üretir."""
    ham: list[dict] = []
    tarihsiz = 0
    not_kanun_tarih: set[tuple[str, str]] = set()

    for n in article.get("degisiklik_notlari") or []:
        recs, skip = parse_degisiklik_notu(n)
        tarihsiz += skip
        for r in recs:
            ham.append(r)
            not_kanun_tarih.add((r["tarih"], r["kanun"]))

    for fp in article.get("dipnotlar") or []:
        recs, skip = parse_dipnot(fp.get("metin") or "")
        tarihsiz += skip
        for r in recs:
            # Aynı tarih + kanun+madde zaten degisiklik_notlari'nda varsa tekrarı önle
            if (r["tarih"], r["kanun"]) in not_kanun_tarih:
                continue
            ham.append(r)

    seen: set[tuple[str, str, str]] = set()
    temiz: list[dict] = []
    for r in ham:
        k = (r["tarih"], r["kanun"], r["aciklama"])
        if k in seen:
            continue
        seen.add(k)
        temiz.append(r)

    temiz.sort(key=lambda r: (r["tarih"], r["kanun"], r["aciklama"]))
    return temiz, tarihsiz


def _base_kanun_map(sources_path: Path = SOURCES_PATH) -> dict[str, str]:
    """Yönetmelik/tebliğ belge_id -> dayandığı derin katman kanunu belge_id eşlemesi."""
    if not sources_path.is_file():
        return {}
    raw = json.loads(sources_path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for v in raw.values():
        if not isinstance(v, dict):
            continue
        bid = v.get("belge_id")
        dayanak = v.get("dayanak") or ""
        if bid and dayanak:
            for no, kanun_bid in DERIN_KANUN_NO_MAP.items():
                if no in dayanak:
                    out[bid] = kanun_bid
                    break
    return out


def _normalize_item(tok: str) -> str:
    s = re.sub(r"\s+", " ", tok.strip())
    low = s.lower()
    if low.startswith("ek "):
        return "Ek " + s[3:].strip().upper() if "/" in s else "Ek " + s[3:].strip()
    if low.startswith("geçici "):
        return "Geçici " + s[7:].strip()
    if "/" in s:
        a, b = s.split("/", 1)
        return f"{a}/{b.upper()}"
    return s


def _expand_items(items_str: str) -> list[str]:
    """'17 ila 21', '18, 19, 20 ve 21', 'ek 1 inci' gibi madde dizilerini açar."""
    cleaned = re.sub(
        r"\s*(?:[’']?\s*)?(?:inci|ıncı|üncü|uncu|nci|ncı|ncü|ncu)\b",
        "",
        items_str,
        flags=re.IGNORECASE,
    )
    # Aralık: "17 ila 21"
    m_range = re.fullmatch(r"\s*(\d+)\s+ila\s+(\d+)\s*", cleaned, re.IGNORECASE)
    if m_range:
        a, b = int(m_range.group(1)), int(m_range.group(2))
        if 1 <= a <= b and (b - a) <= 30:
            return [str(x) for x in range(a, b + 1)]

    parts = re.split(r"\s*(?:,|ve|ile|veya)\s*", cleaned, flags=re.IGNORECASE)
    out: list[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if re.fullmatch(r"(?:(?:ek|geçici)\s+)?\d+(?:/[A-ZÇĞİÖŞÜa-z])?", p, re.IGNORECASE):
            out.append(_normalize_item(p))
    return out


def _resolve_target_doc(
    prefix: str,
    cur_belge_id: str,
    cur_tur: str,
    base_kanun: str | None,
    last_named_doc: tuple[bool, str | None],
) -> tuple[str | None, tuple[bool, str | None]]:
    """Atıf ön ekinden hedef belge_id'yi belirler; emin değilse veya hariciyse None döner."""
    p = prefix.strip()
    low = p.lower()

    # 1. Açık "bu Kanunun / bu Yönetmeliğin / bu Tebliğin"
    if re.search(r"\bbu\s+(?:kanun\w*|yönetmeli\w*|tebliğ\w*)\s*$", low):
        return cur_belge_id, (True, cur_belge_id)

    # 2. Açık belge numarası ("6698 sayılı", "4857 sayılı", "1475 sayılı", "6331 sayılı", veya harici "506 sayılı")
    nos = RE_HARICI_KANUN_NO.findall(p)
    if nos:
        son_no = nos[-1]
        if son_no in DERIN_KANUN_NO_MAP:
            bid = DERIN_KANUN_NO_MAP[son_no]
            return bid, (True, bid)
        # Harici kanun -> derlem dışı
        return None, (True, None)

    # 3. Açık adla anılan derin katman belgeleri (numara olmadan)
    if re.search(r"kişisel\s+verilerin\s+korunması\s+kanun\w*|\bkvkk\b", low):
        return "kvkk", (True, "kvkk")
    if re.search(r"iş\s+sağlığı\s+ve\s+güvenliği\s+kanun\w*|\bisg\s+kanun\w*", low):
        return "isg-kanunu", (True, "isg-kanunu")
    if re.search(r"\biş\s+kanun\w*", low):
        return "is-kanunu", (True, "is-kanunu")

    # 4. "aynı / anılan Kanunun" -> aynı cümlede/bağlamda son anılan Kanun varsa ona bağla
    if re.search(r"\b(?:aynı|anılan)\s+kanun\w*\s*$", low):
        has_named, named_bid = last_named_doc
        if has_named:
            return named_bid, last_named_doc
        if cur_tur == "kanun":
            return cur_belge_id, last_named_doc
        return base_kanun, last_named_doc

    if re.search(r"\b(?:aynı|anılan)\s+(?:yönetmeli\w*|tebliğ\w*)\s*$", low):
        return cur_belge_id, last_named_doc

    # 5. Ön ek içinde başka bir adlandırılmış Kanun/Yönetmelik geçiyorsa (ör. "Borçlar Kanununun", "506 ... Kanununun")
    ext_names = RE_HARICI_BELGE_ADI.findall(p)
    for nm in ext_names:
        nm_low = nm.lower()
        # Tek başına veya yerelleştiriciyle ("Bu Kanunun", "Aynı Yönetmeliğin", "İlgili Kişilerin Kanunun" hariç) ayır
        if nm_low.startswith(("kanun", "yönetmeli", "tebliğ", "aynı ", "anılan ", "bu ")):
            continue
        if any(k in nm_low for k in ("borçlar", "ceza", "medeni", "ticaret", "ihale", "sendika", "sigorta", "harcırah", "vergi", "esnaf", "asker", "terör", "kadro", "dilekçe")):
            return None, (True, None)
        # Tanınmayan özel isimli kanun/yönetmelik -> emin olma, ekleme
        return None, (True, None)

    # 6. Yalın "Kanunun ..." (ör. "Kanunun 13 üncü maddesi"):
    #    Kanun içinde kendisi; yönetmelik/tebliğ içinde dayandığı Kanun!
    if re.search(r"(?:^|[\s,(])kanun(?:un|a|da|dan)?\s*$", low):
        if cur_tur == "kanun":
            return cur_belge_id, (True, cur_belge_id)
        return base_kanun, (True, base_kanun) if base_kanun else last_named_doc

    # 7. Yönetmelik / Tebliğ içinde "Yönetmeliğin N inci maddesi" veya "Tebliğin N inci maddesi"
    if re.search(r"(?:^|[\s,(])yönetmeli[ğg](?:in|e|de|den)?\s*$", low) and cur_tur == "yonetmelik":
        return cur_belge_id, (True, cur_belge_id)
    if re.search(r"(?:^|[\s,(])tebli[ğg](?:in|e|de|den)?\s*$", low) and cur_tur == "teblig":
        return cur_belge_id, (True, cur_belge_id)

    # Kanun içinde belirsiz "ilgili yönetmeliğin N inci maddesi" vb. -> harici/belirsiz, ekleme
    if re.search(r"(?:yönetmeli\w*|tebliğ\w*|tüzü\w*)\s*$", low):
        return None, (True, None)

    # 8. Çıplak madde numarası ("5 inci maddesinde", "17 nci madde"):
    #    Aynı cümle/bent listesi içinde daha önce açıkça adlandırılmış bir belge varsa onu miras al
    if RE_HARICI_KANUN_NO.search(p):
        return None, (True, None)
    if last_named_doc[0]:
        return last_named_doc[1], last_named_doc
    return cur_belge_id, last_named_doc


def _detect_block_doc(
    line: str,
    cur_belge_id: str,
    cur_tur: str,
    base_kanun: str | None,
) -> tuple[bool, str | None]:
    """':' veya ';' ile biten bent başlığı satırının hangi belgeye işaret ettiğini belirler."""
    s = line.strip()
    if not s or s[-1] not in ":;":
        return (False, None)
    if re.search(r"\bbu\s+(?:kanun\w*|yönetmeli\w*|tebliğ\w*)", s, re.IGNORECASE):
        return (True, cur_belge_id)
    nos = RE_HARICI_KANUN_NO.findall(s)
    if nos:
        son_no = nos[-1]
        if son_no in DERIN_KANUN_NO_MAP:
            return (True, DERIN_KANUN_NO_MAP[son_no])
        return (True, None)
    # Başlık yalnız "Kanunun ..." veya başka belge içeriyorsa _resolve_target_doc ile kontrol et
    if re.search(r"\b(?:kanun\w*|yönetmeli\w*|tebliğ\w*)\s*[;:]\s*$", s, re.IGNORECASE):
        bid, _ = _resolve_target_doc(s[:-1], cur_belge_id, cur_tur, base_kanun, (False, None))
        return (True, bid)
    return (False, None)


def extract_outgoing_refs(
    article: dict,
    valid_keys: set[str],
    base_kanun_by_doc: dict[str, str],
) -> list[str]:
    """Madde metninden derlem içinde var olan benzersiz hedef anahtarları çıkarır."""
    bid = article["belge_id"]
    cur_key = f"{bid}:{article['madde_no']}"
    cur_tur = article.get("belge_tur", "kanun")
    base_kanun = base_kanun_by_doc.get(bid)

    raw_text = "\n".join(f.get("metin") or "" for f in article.get("fikralar") or [])
    cleaned_text = RE_INLINE_ANNOT.sub(" ", raw_text)
    cleaned_text = RE_QUOTED_SPAN.sub(" ", cleaned_text)
    cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)

    found: list[str] = []
    seen: set[str] = set()
    block_doc: tuple[bool, str | None] = (False, None)

    for para in cleaned_text.splitlines():
        s_para = para.strip()
        is_bent = bool(re.match(r"^(?:[a-zçğıöşü]{1,2}\)|\d+\))\s*", s_para))
        if not is_bent:
            block_doc = _detect_block_doc(s_para, bid, cur_tur, base_kanun)

        sent_doc: tuple[bool, str | None] = block_doc if is_bent else (False, None)
        prev_end = 0

        for m in RE_MADDE_REF.finditer(para):
            between = para[prev_end:m.start()]
            if "." in between or ";" in between:
                sent_doc = block_doc if is_bent else (False, None)
            prev_end = m.end()

            after = para[m.end():m.end() + 25].lower()
            # Dipnot/değişiklik cümlesi kalıntısı ("... maddesiyle ... değiştirilmiştir") koruması
            if re.match(r"^(?:yle|yla|siyle|sıyla)\b", after):
                continue

            prefix = m.group("prefix")
            target_bid, sent_doc = _resolve_target_doc(
                prefix, bid, cur_tur, base_kanun, sent_doc
            )
            if not target_bid:
                continue

            for item in _expand_items(m.group("items")):
                target_key = f"{target_bid}:{item}"
                if target_key == cur_key:
                    continue
                if target_key in valid_keys and target_key not in seen:
                    seen.add(target_key)
                    found.append(target_key)

        if not is_bent and not block_doc[0]:
            block_doc = (False, None)
        elif is_bent and s_para.endswith((".", "yürürlüğe girer.")) and not s_para.endswith(";"):
            # Alt bent cümlesi bittiğinde yalnız yeni bent yoksa blok sürer; sıradaki düz satır zaten sıfırlar
            pass

    return found


def build_iliskiler(
    articles_path: Path = ARTICLES_PATH,
    sources_path: Path = SOURCES_PATH,
    out_path: Path = OUT_PATH,
) -> tuple[dict[str, dict], dict]:
    """articles.jsonl'den değişiklik geçmişi ve çift yönlü madde ilişkilerini üretir."""
    articles = [
        json.loads(line)
        for line in Path(articles_path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    valid_keys = {f"{a['belge_id']}:{a['madde_no']}" for a in articles}
    base_kanun_by_doc = _base_kanun_map(sources_path)

    result: dict[str, dict] = {}
    outgoing_by_key: dict[str, list[str]] = {}
    tarihsiz_atlanan = 0
    gecmis_madde_sayisi = 0
    toplam_gecmis_kaydi = 0
    belge_stats: dict[str, Counter] = {}

    for a in articles:
        key = f"{a['belge_id']}:{a['madde_no']}"
        st = belge_stats.setdefault(a["belge_id"], Counter())
        st["madde"] += 1

        gecmis, skip = extract_gecmis(a)
        tarihsiz_atlanan += skip
        if gecmis:
            gecmis_madde_sayisi += 1
            toplam_gecmis_kaydi += len(gecmis)
            st["gecmisli_madde"] += 1
            st["gecmis_kaydi"] += len(gecmis)

        refs = extract_outgoing_refs(a, valid_keys, base_kanun_by_doc)
        outgoing_by_key[key] = refs
        result[key] = {"gecmis": gecmis, "iliskili": []}

    # Çift yönlü ilişki ekleme: A atif_yapar B => B atif_alir A
    edge_pairs: dict[str, set[tuple[str, str]]] = {k: set() for k in result}
    yonlu_iliski_sayisi = 0
    for src, targets in outgoing_by_key.items():
        for dst in targets:
            edge_pairs[src].add((dst, "atif_yapar"))
            edge_pairs[dst].add((src, "atif_alir"))
            yonlu_iliski_sayisi += 1
            belge_stats[src.split(":", 1)[0]]["atif_yapar"] += 1
            belge_stats[dst.split(":", 1)[0]]["atif_alir"] += 1

    from src.ingest.chunk import atif as _atif
    def _guvenli_atif(a: dict) -> str:
        try:
            return _atif(a, None)
        except (KeyError, IndexError):   # eksik alanlı kayıt (ör. test verisi): anahtarı göster
            return f"{a['belge_id']}:{a['madde_no']}"

    ad = {f"{a['belge_id']}:{a['madde_no']}": (_guvenli_atif(a), a.get("baslik") or None) for a in articles}
    for k, pairs in edge_pairs.items():
        result[k]["iliskili"] = [
            {"anahtar": dst, "atif": ad[dst][0], "baslik": ad[dst][1], "iliski": rel}
            for dst, rel in sorted(pairs, key=lambda p: (0 if p[1] == "atif_yapar" else 1, p[0]))
        ]

    if out_path is not None:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    stats = {
        "toplam_madde": len(articles),
        "gecmisli_madde": gecmis_madde_sayisi,
        "toplam_gecmis_kaydi": toplam_gecmis_kaydi,
        "tarihsiz_atlanan": tarihsiz_atlanan,
        "yonlu_iliski": yonlu_iliski_sayisi,
        "iliskili_madde": sum(1 for v in result.values() if v["iliskili"]),
        "belge_bazinda": {bid: dict(c) for bid, c in sorted(belge_stats.items())},
    }
    return result, stats


def main() -> None:
    p = argparse.ArgumentParser(description="Derin katman değişiklik geçmişi ve madde ilişkileri çıkarıcısı.")
    p.add_argument("--src", type=Path, default=ARTICLES_PATH)
    p.add_argument("--sources", type=Path, default=SOURCES_PATH)
    p.add_argument("--out", type=Path, default=OUT_PATH)
    args = p.parse_args()

    _, stats = build_iliskiler(args.src, args.sources, args.out)
    print(
        f"Tamamlandı -> {args.out}: {stats['toplam_madde']} madde, "
        f"{stats['gecmisli_madde']} maddede {stats['toplam_gecmis_kaydi']} geçmiş kaydı "
        f"(tarihsiz atlanan={stats['tarihsiz_atlanan']}), "
        f"{stats['yonlu_iliski']} yönlü ilişki ({stats['iliskili_madde']} maddede bağlantı)"
    )
    for bid, c in stats["belge_bazinda"].items():
        print(
            f"  {bid:22s}: madde={c.get('madde', 0):3d}, "
            f"geçmiş={c.get('gecmisli_madde', 0):2d} ({c.get('gecmis_kaydi', 0):3d}), "
            f"atıf_yapar={c.get('atif_yapar', 0):3d}, atıf_alir={c.get('atif_alir', 0):3d}"
        )


if __name__ == "__main__":
    main()
