"""
SATORI ECOSYSTEM — ItachiAssist
================================
itachi_core/plugins/os_watcher.py

OS faoliyat kuzatuvchi plagini.
  - Faol oynani aniqlash (Linux: xdotool, Windows: win32gui)
  - Har 30 soniyada log yuborish
  - Dastur almashuv tarixi

XAVFSIZLIK: Faqat oyna sarlavhalari va dastur nomlari
yoziladi. Klaviatura / sichqoncha harakati YOZILMAYDI.
"""

import asyncio
import logging
import platform
import subprocess
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from event_bus import EventBus
    from plugins.api_client import ApiClient

logger = logging.getLogger("itachi.os_watcher")

WATCH_INTERVAL_SEC = 30  # Har 30 soniyada tekshirish


class OsWatcher:
    """
    Operatsion tizim faoliyatini kuzatuvchi plagin.
    Faqat oyna sarlavhasi va dastur nomini yozadi.
    """

    def __init__(self, bus: "EventBus", api_client: "ApiClient"):
        self.bus = bus
        self.api = api_client
        self._os = platform.system()   # "Linux", "Windows", "Darwin"
        self._running = False
        self._last_window = ""
        self._window_start_time = time.time()
        self._watcher_task: asyncio.Task | None = None

    async def setup(self):
        """Kuzatuvni boshlash."""
        if self._os == "Linux":
            if not self._check_xdotool():
                logger.warning("[OS] xdotool topilmadi. O'rnatish: sudo apt install xdotool")
                return
        elif self._os == "Windows":
            try:
                import win32gui
            except ImportError:
                logger.warning("[OS] pywin32 o'rnatilmagan. O'rnatish: pip install pywin32")
                return

        self._running = True
        self._watcher_task = asyncio.create_task(self._watch_loop())
        logger.info(f"[OS] Kuzatuv boshlandi ({self._os})")

    def _check_xdotool(self) -> bool:
        """xdotool mavjudligini tekshirish."""
        try:
            result = subprocess.run(
                ["which", "xdotool"], capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def _get_active_window_linux(self) -> tuple[str, str]:
        """Linux: xdotool + xprop orqali faol oynani aniqlash."""
        try:
            # 1. Faol oyna ID sini olish
            win_id = subprocess.check_output(
                ["xdotool", "getactivewindow"], text=True,
                stderr=subprocess.DEVNULL
            ).strip()

            # 2. Oyna sarlavhasini olish
            title = subprocess.check_output(
                ["xdotool", "getwindowname", win_id], text=True,
                stderr=subprocess.DEVNULL
            ).strip()

            # 3. Dastur nomini olish (xprop WM_CLASS orqali)
            # Natija: WM_CLASS(STRING) = "code", "Code"
            try:
                wm_raw = subprocess.check_output(
                    ["xprop", "-id", win_id, "WM_CLASS"], text=True,
                    stderr=subprocess.DEVNULL
                ).strip()
                # "code", "Code"  →  oxirgi qiymat → "code"
                parts = wm_raw.split('"')
                # parts = ['WM_CLASS(STRING) = ', 'code', ', ', 'Code', '']
                app_name = parts[1].lower() if len(parts) >= 2 else "unknown"
            except Exception:
                # xprop yo'q bo'lsa sarlavhadan birinchi so'zni olish
                app_name = title.split()[0].lower() if title else "unknown"

            return app_name, title

        except subprocess.CalledProcessError:
            return "unknown", ""
        except Exception as e:
            logger.debug(f"[OS] xdotool xato: {e}")
            return "unknown", ""

    def _get_active_window_windows(self) -> tuple[str, str]:
        """Windows: win32gui orqali faol oynani aniqlash."""
        try:
            import win32gui
            import win32process
            import psutil

            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            try:
                proc = psutil.Process(pid)
                app_name = proc.name().lower().replace(".exe", "")
            except Exception:
                app_name = "unknown"

            return app_name, title
        except Exception as e:
            logger.debug(f"[OS] win32 xato: {e}")
            return "unknown", ""

    def _get_active_window(self) -> tuple[str, str]:
        """OS ga qarab faol oynani aniqlash."""
        if self._os == "Linux":
            return self._get_active_window_linux()
        elif self._os == "Windows":
            return self._get_active_window_windows()
        return "unknown", ""

    async def _watch_loop(self):
        """Asosiy kuzatuv sikli."""
        while self._running:
            try:
                loop = asyncio.get_event_loop()
                app_name, title = await loop.run_in_executor(
                    None, self._get_active_window
                )

                current = f"{app_name}|{title}"

                if current != self._last_window:
                    # Oyna o'zgargan — oldingi oyna vaqtini hisoblash
                    if self._last_window:
                        duration = int(time.time() - self._window_start_time)
                        await self._log_window_change(
                            self._last_window, duration
                        )

                    self._last_window = current
                    self._window_start_time = time.time()
                    logger.debug(f"[OS] Faol oyna: [{app_name}] {title[:50]}")

            except Exception as e:
                logger.debug(f"[OS] Kuzatuv xato: {e}")

            await asyncio.sleep(WATCH_INTERVAL_SEC)

    async def _log_window_change(self, window_key: str, duration_sec: int):
        """Oyna o'zgarishini log qilish."""
        parts = window_key.split("|", 1)
        app = parts[0] if parts else "unknown"
        title = parts[1] if len(parts) > 1 else ""

        self.api.add_log(
            level="INFO",
            category="OS_WINDOW",
            payload={
                "active_app": app,
                "window_title": title[:150],     # Uzun sarlavhalarni qisqartirish
                "duration_sec": duration_sec,
            }
        )

        from event_bus import Events
        await self.bus.emit(Events.LOG_SEND, {
            "category": "OS_WINDOW",
            "app": app,
            "duration": duration_sec
        })

    async def stop(self):
        self._running = False
        if self._watcher_task:
            self._watcher_task.cancel()
