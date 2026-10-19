"""
SATORI ECOSYSTEM — ItachiAssist
================================
itachi_core/event_bus.py

Ekotizim ichidagi barcha modullar bir-biri bilan
shu EventBus orqali muloqot qiladi.
Decoupled (bog'liqliksiz) arxitektura — yangi plagin
qo'shilganda asosiy kodga teginish shart emas.
"""

import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable, Coroutine

logger = logging.getLogger("itachi.event_bus")


class EventBus:
    """
    Asinxron hodisalar avtobusi.
    
    Ishlatish:
        bus = EventBus()
        
        @bus.on("USER_TEXT_SUBMIT")
        async def handle(data):
            print(f"Foydalanuvchi yozdi: {data['text']}")
        
        await bus.emit("USER_TEXT_SUBMIT", {"text": "Salom"})
    """

    def __init__(self):
        self._listeners: dict[str, list[Callable]] = defaultdict(list)
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def on(self, event_name: str):
        """Decorator: hodisaga subscriber qo'shish."""
        def decorator(func: Callable):
            self.subscribe(event_name, func)
            return func
        return decorator

    def subscribe(self, event_name: str, callback: Callable):
        """Hodisaga listener ro'yxatdan o'tkazish."""
        self._listeners[event_name].append(callback)
        logger.debug(f"[EventBus] '{event_name}' hodisasiga subscriber qo'shildi: {callback.__name__}")

    def unsubscribe(self, event_name: str, callback: Callable):
        """Listerni o'chirish."""
        listeners = self._listeners.get(event_name, [])
        if callback in listeners:
            listeners.remove(callback)

    async def emit(self, event_name: str, data: Any = None):
        """
        Hodisani barcha subscriberlarga yuborish.
        Barcha callbacklar parallel ishga tushadi.
        """
        listeners = self._listeners.get(event_name, [])
        if not listeners:
            logger.debug(f"[EventBus] '{event_name}' uchun subscriber yo'q")
            return

        logger.debug(f"[EventBus] '{event_name}' chiqdi → {len(listeners)} ta subscriber")

        tasks = []
        for callback in listeners:
            try:
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(asyncio.create_task(callback(data)))
                else:
                    # Oddiy funksiyani thread pool da ishlatish
                    loop = asyncio.get_event_loop()
                    tasks.append(loop.run_in_executor(None, callback, data))
            except Exception as e:
                logger.error(f"[EventBus] '{event_name}' subscriber xatosi ({callback.__name__}): {e}")

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def emit_sync(self, event_name: str, data: Any = None):
        """
        Sinxron kontekstdan hodisa chiqarish
        (masalan, thread dan).
        """
        loop = self._loop or asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.emit(event_name, data), loop
            )
        else:
            loop.run_until_complete(self.emit(event_name, data))

    def get_listener_count(self, event_name: str) -> int:
        return len(self._listeners.get(event_name, []))


# === GLOBAL HODISA NOMLARI (Constants) ===

class Events:
    """Barcha hodisa nomlari bir joyda — typo dan himoya."""
    
    # C# → Python (UI dan keladi)
    UI_READY            = "UI_READY"
    UI_CLOSED           = "UI_CLOSED"
    USER_TEXT_SUBMIT    = "USER_TEXT_SUBMIT"
    MIC_BUTTON_TOGGLED  = "MIC_BUTTON_TOGGLED"
    EYE_CLICKED         = "EYE_CLICKED"
    
    # Python → C# (UI ga boriladi)
    CMD_WINDOW          = "CMD_WINDOW"
    CMD_EYE_STATE       = "CMD_EYE_STATE"
    CMD_AUDIO_AMP       = "CMD_AUDIO_AMP"
    CMD_CHAT_REPLY      = "CMD_CHAT_REPLY"
    CMD_CHAT_THINKING   = "CMD_CHAT_THINKING"
    
    # Ichki hodisalar
    AGENT_RESPONSE      = "AGENT_RESPONSE"
    VOICE_START         = "VOICE_START"
    VOICE_END           = "VOICE_END"
    SCREEN_CAPTURED     = "SCREEN_CAPTURED"
    LOG_SEND            = "LOG_SEND"
    SHUTDOWN            = "SHUTDOWN"
