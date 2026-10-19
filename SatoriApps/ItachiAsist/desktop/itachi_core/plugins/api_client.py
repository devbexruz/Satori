"""
SATORI ECOSYSTEM — ItachiAssist
================================
itachi_core/plugins/api_client.py

Satori Backend bilan aloqa plagini.
  - Loglarni batch yuborish (POST /api/v1/telemetry/ingest)
  - AI so'rovlarni yuborish (POST /api/v1/agent/ask)
  - Tarmoq xatolarida exponential backoff retry

Phase 3 da to'liq ishlab chiqiladi.
"""

import asyncio
import logging
import uuid
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from event_bus import EventBus

logger = logging.getLogger("itachi.api_client")

BACKEND_URL = "http://127.0.0.1:8765"
APP_SLUG = "itachi-assist"


class ApiClient:
    """
    ItachiAssist backend bilan asinxron HTTP aloqa.
    Tarmoq xatolarida avtomatik retry qiladi.
    """

    def __init__(self, bus: "EventBus", backend_url: str = BACKEND_URL):
        self.bus = bus
        self.backend_url = backend_url
        self.session_id = str(uuid.uuid4())
        self._http = None
        self._log_buffer: list[dict] = []
        self._flush_task: asyncio.Task | None = None
        self._available = False

    async def setup(self):
        """httpx client initsializatsiya."""
        try:
            import httpx
            self._http = httpx.AsyncClient(
                base_url=self.backend_url,
                timeout=httpx.Timeout(10.0),
            )
            # Backend mavjudligini tekshirish
            self._available = await self._check_health()
            if self._available:
                logger.info(f"[API] ✅ Backend ulandi: {self.backend_url}")
                # Loglarni har 10 soniyada yuborish
                self._flush_task = asyncio.create_task(self._auto_flush_loop())
            else:
                logger.warning(f"[API] ⚠️  Backend javob bermadi: {self.backend_url}")
        except ImportError:
            logger.warning("[API] httpx o'rnatilmagan. O'rnatish: pip install httpx")

    async def _check_health(self) -> bool:
        """Backend mavjudligini tekshirish."""
        try:
            response = await self._http.get("/health", timeout=3.0)
            return response.status_code == 200
        except Exception:
            return False

    def add_log(self, level: str, category: str, payload: dict[str, Any]):
        """Log buferiga qo'shish (keyinchalik batch yuboriladi)."""
        self._log_buffer.append({
            "log_level": level,
            "category": category,
            "payload": payload,
        })

    async def flush_logs(self):
        """Buferidagi loglarni backend ga yuborish."""
        if not self._available or not self._http or not self._log_buffer:
            return

        batch = self._log_buffer.copy()
        self._log_buffer.clear()

        try:
            await self._http.post(
                "/api/v1/telemetry/ingest",
                json={
                    "app_slug": APP_SLUG,
                    "session_id": self.session_id,
                    "logs": batch,
                }
            )
            logger.debug(f"[API] {len(batch)} ta log yuborildi")
        except Exception as e:
            logger.warning(f"[API] Log yuborishda xato: {e}")
            # Buferni qaytarish
            self._log_buffer = batch + self._log_buffer

    async def ask_ai(self, prompt: str, include_screen: bool = False,
                     screen_ocr: str = "") -> str:
        """AI agentga so'rov yuborish va javob olish."""
        if not self._available or not self._http:
            return f"[Offline] Backend ulangan emas. So'rov: '{prompt}'"

        payload = {
            "prompt": prompt,
            "persona": "itachi",
            "include_recent_logs": True,
            "log_window_minutes": 30,
        }
        if include_screen and screen_ocr:
            payload["screen_context"] = {"ocr_text": screen_ocr}

        try:
            response = await self._http.post(
                "/api/v1/agent/ask",
                json=payload,
                timeout=30.0,
            )
            data = response.json()
            return data.get("reply", "Javob bo'sh")
        except Exception as e:
            logger.error(f"[API] AI so'rovda xato: {e}")
            return f"[Xato] So'rov yuborishda muammo: {str(e)[:80]}"

    async def _auto_flush_loop(self):
        """Har 10 soniyada loglarni avtomatik yuborish."""
        while True:
            await asyncio.sleep(10)
            await self.flush_logs()

    async def stop(self):
        """Yopishdan oldin barcha loglarni yuborish."""
        if self._flush_task:
            self._flush_task.cancel()
        await self.flush_logs()
        if self._http:
            await self._http.aclose()
