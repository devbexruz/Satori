"""
SATORI ECOSYSTEM — ItachiAssist
================================
itachi_core/plugins/screen_vision.py

Ekran ko'rish plagini.
  1. mss orqali tezkor screenshot (diskka yozilmaydi!)
  2. pytesseract orqali OCR
  3. Faqat foydalanuvchi "include_screen: true" deganda ishlaydi

XAVFSIZLIK: Screenshot faqat xotirada (io.BytesIO),
disk ga hech narsa yozilmaydi, tahlildan so'ng o'chiriladi.
"""

import asyncio
import io
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from event_bus import EventBus
    from ui_bridge import UIBridge

logger = logging.getLogger("itachi.vision")


@dataclass
class ScreenContext:
    """Ekrandan olingan kontekst."""
    ocr_text: str = ""
    width: int = 0
    height: int = 0
    error: str = ""

    @property
    def has_content(self) -> bool:
        return bool(self.ocr_text.strip())


class ScreenVisionPlugin:
    """
    On-Demand ekran ko'rish plagini.
    
    MUHIM: Ekran doimiy yozib borilmaydi.
    Faqat buyruq kelganda bitta screenshot olinadi.
    """

    def __init__(self, bus: "EventBus", bridge: "UIBridge"):
        self.bus = bus
        self.bridge = bridge
        self._mss_available = False
        self._ocr_available = False
        self._last_context: ScreenContext | None = None

    async def setup(self):
        """Kutubxonalar mavjudligini tekshirish."""
        try:
            import mss
            self._mss_available = True
            logger.info("[Vision] ✅ mss mavjud")
        except ImportError:
            logger.warning("[Vision] ⚠️  mss o'rnatilmagan. O'rnatish: pip install mss")

        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            self._ocr_available = True
            logger.info("[Vision] ✅ pytesseract mavjud")
        except Exception:
            logger.warning("[Vision] ⚠️  pytesseract o'rnatilmagan yoki Tesseract topilmadi.")

        # EventBus ga ulash
        from event_bus import Events
        self.bus.subscribe(Events.USER_TEXT_SUBMIT, self._on_user_text)

    async def _on_user_text(self, data: dict):
        """Foydalanuvchi so'rovida include_screen bo'lsa ekran olish."""
        if not data.get("include_screen", False):
            return

        logger.info("[Vision] 📸 Ekran surati olinmoqda...")
        context = await self.capture()
        self._last_context = context

        if context.has_content:
            logger.info(f"[Vision] OCR natija ({len(context.ocr_text)} belgi): {context.ocr_text[:100]}...")
            # Kontekstni EVENT orqali jo'natish
            from event_bus import Events
            await self.bus.emit(Events.SCREEN_CAPTURED, {
                "ocr_text": context.ocr_text,
                "width": context.width,
                "height": context.height,
            })
        else:
            logger.warning(f"[Vision] Ekrandan matn ajratib bo'lmadi. Sabab: {context.error}")

    async def capture(self) -> ScreenContext:
        """
        Ekrandan screenshot olib OCR qilish.
        
        Returns:
            ScreenContext bilan OCR matni va o'lchamlar.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._capture_sync)

    def _capture_sync(self) -> ScreenContext:
        """Blokirovchi screenshot va OCR (thread da ishlaydi)."""
        if not self._mss_available:
            return ScreenContext(error="mss o'rnatilmagan")

        try:
            import mss
            from PIL import Image

            with mss.mss() as sct:
                # Birinchi monitordagi butun ekran
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)

                # PIL Image ga aylantirish (diskka yozmasdan)
                img = Image.frombytes(
                    "RGB",
                    (screenshot.width, screenshot.height),
                    screenshot.rgb
                )

                context = ScreenContext(
                    width=screenshot.width,
                    height=screenshot.height,
                )

                if self._ocr_available:
                    context.ocr_text = self._run_ocr(img)
                else:
                    context.error = "pytesseract mavjud emas"

                # img xotirada — garbage collector o'chiradi
                del img
                return context

        except Exception as e:
            logger.error(f"[Vision] Screenshot xatosi: {e}")
            return ScreenContext(error=str(e))

    def _run_ocr(self, img) -> str:
        """pytesseract bilan OCR."""
        try:
            import pytesseract

            # Ingliz + o'zbek tili
            text = pytesseract.image_to_string(
                img,
                lang="eng+uzb",
                config="--psm 3"  # Avtomatik sahifa segmentatsiyasi
            )
            # Bo'sh qatorlarni siqish
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"[Vision] OCR xatosi: {e}")
            return ""

    def get_last_context(self) -> ScreenContext | None:
        """Oxirgi ekran kontekstini olish."""
        return self._last_context
