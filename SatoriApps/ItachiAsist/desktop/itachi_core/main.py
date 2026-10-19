"""
SATORI ECOSYSTEM — ItachiAssist
================================
itachi_core/main.py

Asosiy kirish nuqtasi. Python Master Process.

Ishlatish:
    python3 main.py
    python3 main.py --headless    # UI siz rejim (test uchun)
    python3 main.py --debug       # Batafsil loglar
"""

import asyncio
import logging
import signal
import sys
import os
import argparse
from pathlib import Path

# Joriy papkani Python path ga qo'shish
sys.path.insert(0, str(Path(__file__).parent))

from event_bus import EventBus, Events
from ui_bridge import UIBridge

# ============================================================
# KONFIGURATSIYA
# ============================================================

# itachi_ui bajariladigan fayl joylashuvi
# (Build qilingandan so'ng to'g'ri yo'l ko'rsatiladi)
_SCRIPT_DIR = Path(__file__).parent
_UI_EXECUTABLE = _SCRIPT_DIR.parent / "itachi_ui" / "bin" / "Release" / "net10.0" / "ItachiUI"
_UI_EXECUTABLE_WIN = _SCRIPT_DIR.parent / "itachi_ui" / "bin" / "Release" / "net10.0" / "ItachiUI.exe"


def _get_ui_path() -> str:
    """OS ga qarab UI yo'lini aniqlash."""
    if sys.platform == "win32":
        return str(_UI_EXECUTABLE_WIN)
    return str(_UI_EXECUTABLE)


# ============================================================
# LOGGING SOZLASH
# ============================================================

def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-8s  %(name)s  —  %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


# ============================================================
# ASOSIY JARAYON
# ============================================================

class ItachiCore:
    """
    ItachiAssist ning asosiy boshqaruv sinfi.
    
    Barcha plaginlar va ko'prikni boshqaradi.
    EventBus orqali ular bir-biri bilan muloqot qiladi.
    """

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.bus = EventBus()
        self.bridge = UIBridge(
            bus=self.bus,
            ui_executable_path=_get_ui_path()
        )
        self._shutdown_event = asyncio.Event()

        # Yüklangan plaginlar ro'yxati
        self._plugins = []

    async def _setup_event_handlers(self):
        """Asosiy hodisa handlerlari."""

        @self.bus.on(Events.UI_READY)
        async def on_ui_ready(data):
            logging.getLogger("itachi").info("✅ UI tayyor! Ko'prik ishlayapti.")
            # UI ni ko'rsatish
            self.bridge.show_window()
            await asyncio.sleep(0.3)
            self.bridge.set_eye_idle()

        @self.bus.on(Events.UI_CLOSED)
        async def on_ui_closed(data):
            logging.getLogger("itachi").info("UI yopildi. Tizim o'chmoqda...")
            self._shutdown_event.set()

        @self.bus.on(Events.USER_TEXT_SUBMIT)
        async def on_user_text(data):
            text = data.get("text", "").strip()
            include_screen = data.get("include_screen", False)
            if not text:
                return

            logger = logging.getLogger("itachi")
            logger.info(f"👤 Foydalanuvchi: {text}")

            # "O'ylayapman" animatsiyasini ko'rsatish
            self.bridge.set_eye_thinking()
            self.bridge.send_chat_thinking(True)

            # Ekran kontekstini olish (agar kerak bo'lsa)
            screen_ocr = ""
            if include_screen:
                screen_captured = asyncio.Event()
                async def on_screen(d):
                    nonlocal screen_ocr
                    screen_ocr = d.get("ocr_text", "")
                    screen_captured.set()
                self.bus.subscribe(Events.SCREEN_CAPTURED, on_screen)
                await self.bus.emit(Events.USER_TEXT_SUBMIT, {
                    "text": text, "include_screen": True, "_internal": True
                })
                try:
                    await asyncio.wait_for(screen_captured.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    pass

            # AI ga so'rov yuborish
            if hasattr(self, "api_client") and self.api_client and self.api_client._available:
                reply = await self.api_client.ask_ai(
                    prompt=text,
                    include_screen=include_screen,
                    screen_ocr=screen_ocr,
                )
            else:
                reply = (
                    f"Backend ulangan emas. So'rovingiz: '{text[:60]}'\n"
                    f"Backend ni ishga tushiring: uvicorn app.main:app"
                )

            await self.bus.emit(Events.AGENT_RESPONSE, {
                "text": reply,
                "source": "ai"
            })

        @self.bus.on(Events.AGENT_RESPONSE)
        async def on_agent_response(data):
            text = data.get("text", "")
            # Javobni UI ga yuborish
            self.bridge.send_chat_thinking(False)
            self.bridge.set_eye_mangekyou()
            self.bridge.send_chat_reply(text)
            # Ovoz plag'ini ulangandan so'ng shu yerda gapiradi (Phase 2)
            await asyncio.sleep(2.0)
            self.bridge.set_eye_idle()

        @self.bus.on(Events.SHUTDOWN)
        async def on_shutdown(data):
            self._shutdown_event.set()

    async def _load_plugins(self):
        """Plaginlarni yuklash va EventBus ga ulash."""
        logger = logging.getLogger("itachi.plugins")

        # === API Client (Phase 3) ===
        try:
            from plugins.api_client import ApiClient
            self.api_client = ApiClient(self.bus)
            await self.api_client.setup()
            self._plugins.append(self.api_client)
            logger.info("[Plugins] ✅ ApiClient yuklandi")
        except Exception as e:
            self.api_client = None
            logger.warning(f"[Plugins] ApiClient yuklanmadi: {e}")

        # === OS Watcher (Phase 3) ===
        try:
            from plugins.os_watcher import OsWatcher
            os_watch = OsWatcher(self.bus, self.api_client) if self.api_client else None
            if os_watch:
                await os_watch.setup()
                self._plugins.append(os_watch)
                logger.info("[Plugins] ✅ OsWatcher yuklandi")
        except Exception as e:
            logger.warning(f"[Plugins] OsWatcher yuklanmadi: {e}")

        # === Screen Vision (Phase 2) ===
        try:
            from plugins.screen_vision import ScreenVisionPlugin
            vision = ScreenVisionPlugin(self.bus, self.bridge)
            await vision.setup()
            self._plugins.append(vision)
            logger.info("[Plugins] ✅ ScreenVision yuklandi")
        except Exception as e:
            logger.warning(f"[Plugins] ScreenVision yuklanmadi: {e}")

        # === Voice RVC (Phase 2) ===
        try:
            from plugins.voice_rvc import VoicePlugin
            voice = VoicePlugin(self.bus, self.bridge)
            await voice.setup()
            self._plugins.append(voice)
            logger.info("[Plugins] ✅ VoicePlugin yuklandi")
        except Exception as e:
            logger.warning(f"[Plugins] VoicePlugin yuklanmadi: {e}")

        logger.info(f"[Plugins] Jami {len(self._plugins)} ta plagin yuklandi")

    async def run(self):
        """Asosiy ishga tushirish sikli."""
        logger = logging.getLogger("itachi")
        logger.info("=" * 50)
        logger.info("  🌌 SATORI — ItachiAssist Core v1.0")
        logger.info("=" * 50)

        # EventBus loop ni sozlash
        loop = asyncio.get_event_loop()
        self.bus.set_loop(loop)

        # Hodisa handlerlarini ulash
        await self._setup_event_handlers()

        # Plaginlarni yuklash
        await self._load_plugins()

        if not self.headless:
            # C# UI ni ishga tushirish
            logger.info("🚀 ItachiUI (C# Avalonia) ishga tushmoqda...")
            await self.bridge.start()
        else:
            logger.info("⚠️  Headless rejim — UI ishga tushirilmadi")
            # Headless rejimda test uchun stdin dan o'qish
            asyncio.create_task(self._headless_input_loop())

        # SIGINT/SIGTERM uchun signal handler
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig, lambda: asyncio.create_task(self._graceful_shutdown())
            )

        logger.info("✅ ItachiAssist tayyor. To'xtatish uchun Ctrl+C bosing.")
        logger.info("-" * 50)

        # O'chish signalini kutish
        await self._shutdown_event.wait()

        logger.info("👋 ItachiAssist o'chmoqda...")

    async def _headless_input_loop(self):
        """Headless rejimda konsoldan input o'qish (test uchun)."""
        print("\n[Headless] Matn yozing (chiqish: 'quit'):")
        loop = asyncio.get_event_loop()
        while not self._shutdown_event.is_set():
            try:
                line = await loop.run_in_executor(None, sys.stdin.readline)
                line = line.strip()
                if line.lower() in ("quit", "exit", "q"):
                    self._shutdown_event.set()
                    break
                if line:
                    await self.bus.emit(Events.USER_TEXT_SUBMIT, {
                        "text": line,
                        "include_screen": False
                    })
            except (EOFError, KeyboardInterrupt):
                self._shutdown_event.set()
                break

    async def _graceful_shutdown(self):
        """Tizimni to'g'ri yopish."""
        logging.getLogger("itachi").info("⚡ To'xtatish signali...")
        await self.bridge.stop()
        self._shutdown_event.set()


# ============================================================
# ENTRY POINT
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="ItachiAssist — Satori AI Agent"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="UI siz rejimda ishga tushirish (test uchun)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Batafsil log chiqarish"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging(debug=args.debug)

    core = ItachiCore(headless=args.headless)

    try:
        asyncio.run(core.run())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.getLogger("itachi").critical(f"Kutilmagan xato: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
