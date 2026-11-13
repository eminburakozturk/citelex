"""İstek sınırı: istemci (IP) başına kayan pencere + tüm istemciler için günlük LLM tavanı.

Amaç: halka açık API'de tek bir istemcinin ücretsiz LLM kotasını tüketmesini engellemek.
Bellekte tutulur (tek süreç); süreç yeniden başlayınca sıfırlanır. Birden çok süreç/kopya
çalıştırılacaksa ortak bir depo (Redis) gerekir — bu ölçekte gereksiz.
"""
from __future__ import annotations

import threading
import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, per_minute: int = 10, per_day: int = 200, global_per_day: int = 0, max_clients: int = 10000):
        self.per_minute, self.per_day, self.global_per_day = per_minute, per_day, global_per_day
        self.max_clients = max_clients
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._global: deque[float] = deque()
        self._lock = threading.Lock()

    def check(self, client: str, now: float | None = None) -> tuple[bool, int, str]:
        """(izin, kaç saniye sonra tekrar denenebilir, neden). İzin verilirse istek sayılır."""
        now = time.time() if now is None else now
        with self._lock:
            while self._global and now - self._global[0] >= 86400:
                self._global.popleft()
            if self.global_per_day and len(self._global) >= self.global_per_day:
                return False, int(86400 - (now - self._global[0])) + 1, "gunluk_toplam"
            if len(self._hits) > self.max_clients:  # bellek sınırı: süresi dolmuş istemcileri at
                for k in [k for k, q in self._hits.items() if not q or now - q[-1] >= 86400]:
                    del self._hits[k]
            q = self._hits[client]
            while q and now - q[0] >= 86400:
                q.popleft()
            if self.per_day and len(q) >= self.per_day:
                return False, int(86400 - (now - q[0])) + 1, "gunluk"
            son_dk = [t for t in q if now - t < 60]
            if self.per_minute and len(son_dk) >= self.per_minute:
                return False, int(60 - (now - son_dk[0])) + 1, "dakika"
            q.append(now)
            self._global.append(now)
            return True, 0, ""
