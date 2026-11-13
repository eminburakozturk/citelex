"""Citelex MCP sunucusu: mevzuat_ara ve madde_getir araçlarını MCP istemcilerine (Claude Desktop, Cursor vb.) açar.

Araçlar src/tools.py'deki ortak katmandır (API ve LangGraph ajanı da aynısını kullanır). Sunucu LLM çağırmaz:
istemci model kaynakları alır, cevabı kendisi yazar; her kaynakta atıf anahtarı ve resmî kaynak bilgisi vardır.
Eşik (configs/answer.json) uygulanır: derlemle ilgisiz soruya kaynak yerine "kapsam dışı" döner.

Çalıştırma (stdio):  python -m src.mcp_server
Claude Desktop yapılandırması (claude_desktop_config.json):
  {"mcpServers": {"citelex": {"command": "C:\\\\...\\\\envs\\\\citelex\\\\python.exe", "args": ["-m", "src.mcp_server"],
                              "cwd": "C:\\\\...\\\\citelex"}}}
Gereken: Qdrant (yerel ya da QDRANT_URL) + bge-m3 (ilk çağrıda yüklenir).
"""
from __future__ import annotations

import os
import threading
from typing import Literal

from mcp.server import MCPServer

from src.tools import AracHatasi, madde_getir, mevzuat_ara

mcp = MCPServer(
    name="citelex",
    instructions=("Türk mevzuatı (KVKK 6698, İş Kanunu 4857, İSG Kanunu 6331, ilgili yönetmelik/tebliğler) ve KVKK Kurul "
                  "kararları üzerinde kaynak arama. Cevap yazarken YALNIZ dönen kaynak metinlerine dayan ve her bilgiyi "
                  "atıf (ör. '6698 s. KVKK m. 5') ile ver; kaynak yetmiyorsa bilmediğini söyle. Hukuki tavsiye değildir."),
)

_lock = threading.Lock()
_searcher = None
_esik = None


def _get():
    global _searcher, _esik
    with _lock:
        if _searcher is None:
            from src.generate.answer import load_cfg
            from src.index.embed import Embedder
            from src.retrieve.search import Searcher
            _searcher = Searcher("hibrit", Embedder(device=os.environ.get("CITELEX_EMBED_DEVICE") or None))
            _esik = load_cfg().get("esik")
    return _searcher, _esik


@mcp.tool(name="mevzuat_ara", description="Türk mevzuatında ve KVKK Kurul kararlarında soruyla ilgili kaynakları ara. Numaralı kaynak "
                      "listesi döner (atıf, atıf anahtarı, metin). Tam metin için madde_getir'i anahtarla çağır.")
def mevzuat_ara_araci(soru: str, turler: list[Literal["kanun", "yonetmelik", "teblig", "karar"]] | None = None,
                      k: int = 5) -> dict:
    s, esik = _get()
    try:
        return mevzuat_ara(s, soru, turler, max(1, min(k, 10)), esik=esik)
    except AracHatasi as e:
        return {"hata": str(e)}


@mcp.tool(name="madde_getir", description="Bir maddenin veya Kurul kararının tam metnini getir. anahtar: 'belge_id:madde_no' "
                      "(ör. 'kvkk:5', 'is-kanunu:41') veya karar için 'kvkk-karar-YYYY-N'.")
def madde_getir_araci(anahtar: str) -> dict:
    s, _ = _get()
    try:
        return madde_getir(s, anahtar)
    except AracHatasi as e:
        return {"hata": str(e)}


if __name__ == "__main__":
    mcp.run("stdio")
