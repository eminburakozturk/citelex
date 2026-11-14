"""LangGraph ajan modu: bağlam yetmiyorsa soruyu yeniden yazıp tekrar ara (en çok 1 kez).

Tek adımlı hat (src/generate/answer.py): ara -> eşik -> LLM -> doğrula. "Bilmiyorum" iki yerden çıkar:
arama eşiği (soru derleme yakın değil) ve LLM (CEVAP_YOK: kaynaklar yetmiyor). Ajan yalnız bu iki durumda devreye girer:

  ara ──(eşik altı)──────────────► yeniden_yaz ──► ara (2. deneme; eşik yine uygulanır) ──► ...
   │                                   ▲
   └─► cevapla ──(CEVAP_YOK, deneme<2)─┘
             └──(cevap ya da deneme bitti)──► son

Yeniden yazma: soru, Türk mevzuatı terimleriyle bir arama sorgusuna çevrilir (kanun adı, hukuki kavram). İkinci
aramanın kaynakları ilkiyle birleştirilir (tekrarlar atılır, bağlam bütçesi korunur); cevap HER ZAMAN özgün soruya
yazılır ve aynı atıf doğrulamasından geçer. Böylece ek LLM çağrısı yalnız "bilmiyorum" durumlarında yapılır.
Risk: yeniden yazma kapsam dışı soruyu derleme "yaklaştırıp" uydurma cevaba yol açabilir — eval'de kapsam dışı ret
ayrıca ölçülür. Araçlar src/tools.py ile aynı arama katmanını kullanır.

Kullanım: python -m src.agent "İşveren çalışanın parmak izini alabilir mi?" --llm openrouter:deepseek/deepseek-v4.1-flash-1017
"""
from __future__ import annotations

import argparse
import time
from typing import TypedDict

from langgraph.graph import END, StateGraph

from src import trace
from src.generate import prompt
from src.generate.answer import DISCLAIMER, GENIS_UYARI, Answerer, build_context, source_key
from src.retrieve.search import trim_context

MAX_DENEME = 2
REWRITE_SYSTEM = """Kullanıcının sorusunu Türk mevzuatında (KVKK 6698, İş Kanunu 4857, İSG Kanunu 6331, ilgili
yönetmelik/tebliğler ve KVKK Kurul kararları) arama yapmak için TEK bir arama sorgusuna çevir.
Gündelik ifadeleri hukuki terimlere çevir (ör. "parmak izi" -> "biyometrik veri, özel nitelikli kişisel veri"),
ilgili kanun adını ekle. Sorunun konusunu DEĞİŞTİRME, yeni olgu ekleme. Yalnız sorguyu yaz, açıklama yazma."""


class Durum(TypedDict, total=False):
    soru: str
    sorgu: str
    deneme: int
    hits: list
    meta: dict
    ham: str
    sorgular: list[str]
    sonuc: dict
    genis_denendi: bool
    arama_sn: float
    llm_sn: float
    turler: list[str] | None


def _birlestir(eski: list, yeni: list) -> list:
    """Yeni aramanın kaynaklarını eklerken tekrarları at; mevzuat önde, karar sonda; bağlam bütçesi korunur."""
    gor, out = set(), []
    for h in [*eski, *yeni]:
        k = (source_key(h.payload), h.payload.get("chunk_id"))
        if k not in gor:
            gor.add(k)
            out.append(h)
    ctx = {"mevzuat": [h for h in out if h.payload["belge_tur"] != "karar"],
           "karar": [h for h in out if h.payload["belge_tur"] == "karar"]}
    ctx = trim_context(ctx)
    return ctx["mevzuat"] + ctx["karar"]


def build_graph(ans: Answerer):
    esik = ans.cfg.get("esik")

    def ara(d: Durum) -> Durum:
        t = time.time()
        with ans._lock:
            hits, meta = build_context(ans.searcher, d["sorgu"], esik, d.get("turler"), genis_yedek=False)
        eslesti = esik is None or meta["dense_top1"] >= esik
        hits = _birlestir(d.get("hits", []), hits if eslesti else [])
        return {"hits": hits, "meta": meta | {"esik_gecti": eslesti or bool(d.get("hits"))},
                "deneme": d.get("deneme", 0) + 1, "arama_sn": d.get("arama_sn", 0.0) + time.time() - t}

    def genis_ara(d: Durum) -> Durum:
        """Son çare: derin katman (yeniden yazılmış sorguyla da) eşiği geçemedi -> özgün soruyla geniş katman."""
        t = time.time()
        with ans._lock:
            hits, meta = build_context(ans.searcher, d["soru"], esik, d.get("turler"), genis_yedek=True)
        gecti = meta["kanallar"] == ["genis"]
        return {"hits": hits if gecti else d.get("hits", []), "meta": (meta if gecti else d["meta"]) | {"esik_gecti": gecti},
                "arama_sn": d.get("arama_sn", 0.0) + time.time() - t, "genis_denendi": True}

    def genisten_sonra(d: Durum) -> str:
        return "cevapla" if d["meta"]["esik_gecti"] else END

    def cevapla(d: Durum) -> Durum:
        t = time.time()
        ham = ans.llm.generate(prompt.SYSTEM, prompt.build_user(d["soru"], d["hits"]))
        return {"ham": ham, "llm_sn": d.get("llm_sn", 0.0) + time.time() - t}

    def yeniden_yaz(d: Durum) -> Durum:
        t = time.time()
        q = ans.llm.generate(REWRITE_SYSTEM, d["soru"], max_tokens=120).strip().splitlines()[0][:300]
        return {"sorgu": q, "sorgular": [*d.get("sorgular", []), q], "llm_sn": d.get("llm_sn", 0.0) + time.time() - t}

    def aramadan_sonra(d: Durum) -> str:
        if d["meta"]["esik_gecti"]:
            return "cevapla"
        if d["deneme"] < MAX_DENEME:
            return "yeniden_yaz"
        return "genis_ara" if getattr(ans.searcher, "genis", None) is not None and not d.get("genis_denendi") else END

    def cevaptan_sonra(d: Durum) -> str:
        bilmiyor = d["ham"].lstrip().upper().startswith(prompt.NO_ANSWER)
        return "yeniden_yaz" if bilmiyor and d["deneme"] < MAX_DENEME else END

    g = StateGraph(Durum)
    g.add_node("ara", ara)
    g.add_node("cevapla", cevapla)
    g.add_node("yeniden_yaz", yeniden_yaz)
    g.add_node("genis_ara", genis_ara)
    g.set_entry_point("ara")
    g.add_conditional_edges("ara", aramadan_sonra, {"cevapla": "cevapla", "yeniden_yaz": "yeniden_yaz",
                                                    "genis_ara": "genis_ara", END: END})
    g.add_conditional_edges("genis_ara", genisten_sonra, {"cevapla": "cevapla", END: END})
    g.add_conditional_edges("cevapla", cevaptan_sonra, {"yeniden_yaz": "yeniden_yaz", END: END})
    g.add_edge("yeniden_yaz", "ara")
    return g.compile()


class AgentAnswerer:
    """Answerer ile aynı arayüz (answer(soru) -> dict); eval/run_eval.py --ajan ile ölçülür."""

    def __init__(self, ans: Answerer):
        self.ans, self.llm, self.cfg, self.searcher = ans, ans.llm, ans.cfg, ans.searcher
        self.graph = build_graph(ans)

    def answer(self, query: str, turler=None) -> dict:
        root = trace.Span("sor", **{"citelex.akis": False, "citelex.ajan": True})
        out = None
        try:
            out = self._answer(query, turler)
            root.set(**{"citelex.ajan_deneme": out.get("ajan_deneme"), "citelex.ajan_sorgular": out.get("ajan_sorgular")})
            return out
        except Exception as e:
            root.error(e)
            raise
        finally:
            self.ans._trace_end(root, query, turler, out, akis=False)

    def _answer(self, query: str, turler=None) -> dict:
        t0 = time.time()
        d = self.graph.invoke({"soru": query, "sorgu": query, "sorgular": [], "turler": turler})
        base = {"soru": query, "llm": self.llm.name + " (ajan)", **{k: d["meta"][k] for k in ("dense_top1", "kanal_top1", "kanallar")},
                "esik": self.cfg.get("esik"), "baglam": [h.payload["atif"] for h in d["hits"]],
                "baglam_anahtar": [source_key(h.payload) for h in d["hits"]], "arama_sn": round(d.get("arama_sn", 0.0), 2),
                "uyari": DISCLAIMER + (" " + GENIS_UYARI if d["meta"]["kanallar"] == ["genis"] else ""),
                "derlem_tarihi": self.cfg.get("derlem_tarihi"),
                "ajan_deneme": d["deneme"], "ajan_sorgular": d.get("sorgular", [])}
        if "ham" not in d:   # iki aramada da eşik geçilmedi
            return {**base, "bilmiyorum": True, "bilmiyorum_katmani": "arama_esigi", "cevap": prompt.NO_ANSWER_TEXT,
                    "neden": "Soru, derlemdeki kaynaklara yeterince yakın değil.", "kaynaklar": [], "gecersiz_atif": [],
                    "sure_sn": round(time.time() - t0, 2)}
        out = self.ans.finalize(d["ham"], d["hits"], base, d.get("llm_sn", 0.0))
        out["sure_sn"] = round(time.time() - t0, 2)
        return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("soru")
    ap.add_argument("--llm", default="openrouter")
    args = ap.parse_args()
    a = AgentAnswerer(Answerer(args.llm)).answer(args.soru)
    print(a["cevap"], "\n", [k["atif"] for k in a.get("kaynaklar", [])], "\nsorgular:", a["ajan_sorgular"],
          "deneme:", a["ajan_deneme"], f"{a['sure_sn']} sn")


if __name__ == "__main__":
    main()
