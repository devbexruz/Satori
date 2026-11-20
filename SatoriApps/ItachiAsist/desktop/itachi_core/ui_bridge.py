"""
SATORI ECOSYSTEM — ItachiAssist
================================
itachi_core/ui_bridge.py

Python (Master) ↔ C# Avalonia (Puppet) o'rtasidagi
stdin/stdout orqali NDJSON protokoli.

PROTOKOL:
  Python → C# : child process ning stdin ga JSON + '\n'
  C# → Python : child process ning stdout dan JSON + '\n'

Barcha xabarlar newline bilan ajratilgan JSON (NDJSON).
"""

import asyncio
import json
import logging
import subprocess
import sys
import os
from pathlib import Path
from typing import Any

from event_bus import EventBus, Events

logger = logging.getLogger("itachi.ui_bridge")


class UIBridge:
    """
    C# Avalonia UI bilan aloqa ko'prigi.
    
    C# dasturini subprocess sifatida ishga tushiradi
    va stdin/stdout orqali JSON xabarlar yuboradi/qabul qiladi.
    """

    def __init__(self, bus: EventBus, ui_executable_path: str):
        self.bus = bus
        self.ui_path = Path(ui_executable_path)
        self._process: subprocess.Popen | None = None
        self._reader_task: asyncio.Task | None = None
        self._is_running = False

    async def start(self):
        """C# UI ni ishga tushirish va stdout o'qishni boshlash."""
        if not self.ui_path.exists():
            logger.warning(
                f"[UIBridge] UI bajariladigan fayl topilmadi: {self.ui_path}\n"
                f"          UI olmagan rejimda davom etilmoqda (headless mode)."
            )
            return

        try:
            self._process = subprocess.Popen(
                [str(self.ui_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                bufsize=1,          # Line-buffered
            )
            self._is_running = True
            logger.info(f"[UIBridge] C# UI ishga tushdi (PID: {self._process.pid})")

            # Stdout ni asinxron o'qish
            loop = asyncio.get_event_loop()
            self._reader_task = loop.run_in_executor(None, self._read_stdout_blocking)

        except FileNotFoundError:
            logger.error(f"[UIBridge] UI fayli topilmadi: {self.ui_path}")
        except Exception as e:
            logger.error(f"[UIBridge] UI ishga tushishda xato: {e}")

    def _read_stdout_blocking(self):
        """
        C# stdout ni blokirovchi tarzda o'qish (thread da ishlaydi).
        Har bir qator — alohida JSON hodisa.
        """
        if not self._process or not self._process.stdout:
            return

        for line in self._process.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                event_data = json.loads(line)
                event_name = event_data.get("event", "UNKNOWN")
                logger.debug(f"[UIBridge] ← C#: {line}")
                # EventBus ga sinxron yuborish (biz thread da turibmiz)
                self.bus.emit_sync(event_name, event_data)
            except json.JSONDecodeError:
                logger.warning(f"[UIBridge] Noto'g'ri JSON: {line!r}")
            except Exception as e:
                logger.error(f"[UIBridge] Hodisani qayta ishlashda xato: {e}")

        logger.info("[UIBridge] C# UI jarayoni tugadi.")
        self._is_running = False
        self.bus.emit_sync(Events.UI_CLOSED, {})

    def send(self, cmd: dict[str, Any]):
        """
        C# UI ga buyruq yuborish.
        
        Misol:
            bridge.send({"cmd": "EYE_STATE", "mode": "MANGEKYOU", "spin_speed": 6.5})
        """
        if not self._process or not self._process.stdin:
            logger.debug(f"[UIBridge] UI yo'q, buyruq yuborilmadi: {cmd}")
            return

        try:
            payload = json.dumps(cmd, ensure_ascii=False) + "\n"
            self._process.stdin.write(payload)
            self._process.stdin.flush()
            logger.debug(f"[UIBridge] → C#: {payload.strip()}")
        except (BrokenPipeError, OSError) as e:
            logger.warning(f"[UIBridge] UI ulanishi uzildi: {e}")
            self._is_running = False

    # === Qulay yordamchi metodlar ===

    def show_window(self, position: str = "BOTTOM_RIGHT"):
        self.send({"cmd": "WINDOW", "action": "SHOW", "position": position})

    def hide_window(self):
        self.send({"cmd": "WINDOW", "action": "HIDE"})

    def set_eye_idle(self, spin_speed: float = 1.0):
        self.send({
            "cmd": "EYE_STATE",
            "mode": "IDLE",
            "spin_speed": spin_speed,
            "glow": "#AAFF0000"
        })

    def set_eye_thinking(self):
        self.send({
            "cmd": "EYE_STATE",
            "mode": "THINKING",
            "spin_speed": 3.5,
            "glow": "#FFAA0000"
        })

    def set_eye_mangekyou(self):
        self.send({
            "cmd": "EYE_STATE",
            "mode": "MANGEKYOU",
            "spin_speed": 6.5,
            "glow": "#FFFF0000"
        })

    def set_eyes_opacity(self, opacity: float):
        """
        Itachining ko'zlar saffoligini (0 dan 100 gacha) o'rnatish.
        0: ko'zlar o'chiq
        100: Sharingan ko'zlari to'liq yonadi
        """
        self.send({
            "cmd": "EYE_OPACITY",
            "opacity": opacity
        })

    def trigger_wake_animation(self):
        """
        'Itachi' yoki 'Hey Itachi' eshitilganda chaqiriladi.
        Ko'zlar 0 dan 100% gacha Ease-Out bilan chaqnaydi,
        so'ngra 80% gacha Ease-In bilan o'rnashadi.
        Itachining o'zi 50% dan 80% gacha ko'tariladi.
        """
        self.send({"cmd": "WAKE_UP"})

    def set_audio_amplitude(self, value: float):
        """Ovoz amplitudasi (0.0 → 1.0) — neon pulsatsiya uchun."""
        self.send({"cmd": "AUDIO_AMP", "value": round(value, 3)})

    def send_chat_reply(self, text: str, typing_effect: bool = True):
        self.send({
            "cmd": "CHAT_REPLY",
            "text": text,
            "typing_effect": typing_effect
        })

    def send_chat_thinking(self, visible: bool = True):
        self.send({"cmd": "CHAT_THINKING", "visible": visible})

    async def stop(self):
        """UI jarayonini to'xtatish."""
        self._is_running = False
        if self._process and self._process.poll() is None:
            try:
                self.send({"cmd": "SHUTDOWN"})
                await asyncio.sleep(0.5)
                self._process.terminate()
                await asyncio.sleep(0.5)
                if self._process.poll() is None:
                    self._process.kill()
            except Exception as e:
                logger.warning(f"[UIBridge] UI to'xtatishda xato: {e}")

    @property
    def is_running(self) -> bool:
        return self._is_running and (
            self._process is not None and self._process.poll() is None
        )
