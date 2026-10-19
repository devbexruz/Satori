"""
SATORI ECOSYSTEM — ItachiAssist
================================
itachi_core/plugins/voice_rvc.py

Ovoz sintez plagini.
  1. Edge-TTS  → O'zbekcha matnni audio ga aylantiradi
  2. RVC v2    → Audio ni Itachi Uchiha tembrига o'tkazadi
  3. Amplituda → Ovoz kuchi (RMS) ni UI ga real-vaqtda uzatadi

PHASE 2 da to'liq ishlab chiqiladi.
Hozir stub (skeleton) ko'rinishida.
"""

import asyncio
import io
import logging
import time
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from event_bus import EventBus
    from ui_bridge import UIBridge

logger = logging.getLogger("itachi.voice")


class VoicePlugin:
    """
    Matn → Ovoz plagini.
    
    Ishlatish:
        plugin = VoicePlugin(bus, bridge)
        await plugin.setup()
        await plugin.speak("Salom, men Itachiman.")
    """

    EDGE_TTS_VOICE = "uz-UZ-SardorNeural"
    EDGE_TTS_RATE  = "-12%"
    EDGE_TTS_PITCH = "-5Hz"
    RVC_MODEL_PATH = "models/itachi.pth"     # Phase 2 da joylashtiriladi
    AMPLITUDE_INTERVAL = 0.05                 # 50ms da bir marta

    def __init__(self, bus: "EventBus", bridge: "UIBridge"):
        self.bus = bus
        self.bridge = bridge
        self._tts_available = False
        self._rvc_available = False

    async def setup(self):
        """Kutubxonalar mavjudligini tekshirish."""
        # Edge-TTS
        try:
            import edge_tts
            self._tts_available = True
            logger.info("[Voice] ✅ edge-tts mavjud")
        except ImportError:
            logger.warning("[Voice] ⚠️  edge-tts o'rnatilmagan. O'rnatish: pip install edge-tts")

        # RVC
        try:
            import rvc
            self._rvc_available = True
            logger.info("[Voice] ✅ RVC mavjud")
        except ImportError:
            logger.warning("[Voice] ⚠️  RVC o'rnatilmagan. Faqat Edge-TTS bilan ishlaydi.")

        # EventBus ga ulash
        from event_bus import Events
        self.bus.subscribe(Events.AGENT_RESPONSE, self._on_agent_response)

    async def _on_agent_response(self, data: dict):
        """Agent javob berganda ovozda gapirish."""
        text = data.get("text", "")
        if text:
            await self.speak(text)

    async def speak(self, text: str):
        """
        Matnni ovozga aylantirish va o'ynатish.
        
        Jarayon:
          1. Edge-TTS → WAV/MP3 bytes (io.BytesIO)
          2. [Agar RVC bor] → Itachi tembri
          3. pygame/sounddevice orqali o'ynатish
          4. O'ynаtish davomida amplituda → UI ga
        """
        if not text.strip():
            return

        logger.info(f"[Voice] 🎙️  Gapirmoqda: {text[:50]}...")

        # UI ga Mangekyou va "thinking" ko'rsatish
        self.bridge.set_eye_mangekyou()

        if self._tts_available:
            try:
                audio_data = await self._synthesize_tts(text)
                if self._rvc_available:
                    audio_data = await self._apply_rvc(audio_data)
                await self._play_with_amplitude(audio_data)
            except Exception as e:
                logger.error(f"[Voice] Ovoz xatosi: {e}")
                await self._fallback_speak(text)
        else:
            await self._fallback_speak(text)

        # Gapirish tugagach idle ga qaytish
        self.bridge.set_eye_idle()

    async def _synthesize_tts(self, text: str) -> bytes:
        """Edge-TTS orqali audio generatsiya."""
        import edge_tts

        communicate = edge_tts.Communicate(
            text=text,
            voice=self.EDGE_TTS_VOICE,
            rate=self.EDGE_TTS_RATE,
            pitch=self.EDGE_TTS_PITCH,
        )

        buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buffer.write(chunk["data"])

        buffer.seek(0)
        logger.debug(f"[Voice] TTS: {buffer.getbuffer().nbytes} bytes")
        return buffer.read()

    async def _apply_rvc(self, audio_data: bytes) -> bytes:
        """RVC v2 orqali Itachi tembrini qo'llash (Phase 2)."""
        # TODO: Phase 2 da amalga oshiriladi
        logger.debug("[Voice] RVC: hozir stub, Edge-TTS audio qaytarilmoqda")
        return audio_data

    async def _play_with_amplitude(self, audio_data: bytes):
        """
        Audio o'ynatish + real-vaqt amplituda UI ga.
        pygame yoki sounddevice ishlatiladi.
        """
        try:
            import pygame
            await self._play_pygame(audio_data)
        except ImportError:
            try:
                import sounddevice as sd
                import numpy as np
                await self._play_sounddevice(audio_data)
            except ImportError:
                logger.warning("[Voice] pygame yoki sounddevice o'rnatilmagan.")
                await self._simulate_amplitude()

    async def _play_pygame(self, audio_data: bytes):
        """pygame orqali o'ynатish."""
        import pygame
        import threading

        pygame.mixer.init()
        sound = pygame.mixer.Sound(io.BytesIO(audio_data))
        channel = sound.play()

        # Amplitude simulatsiyasi (pygame real amplituda bermaydi)
        duration = sound.get_length()
        await self._simulate_amplitude(duration)
        while channel.get_busy():
            await asyncio.sleep(0.05)

    async def _play_sounddevice(self, audio_data: bytes):
        """sounddevice orqali numpy array bilan o'ynатish."""
        import sounddevice as sd
        import numpy as np
        import wave

        # WAV formatidan numpy array
        with wave.open(io.BytesIO(audio_data)) as wf:
            frames = wf.readframes(wf.getnframes())
            sample_rate = wf.getframerate()
            audio_array = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

        # Chunklab o'ynатish va amplituda yuborish
        chunk_size = int(sample_rate * self.AMPLITUDE_INTERVAL)
        for i in range(0, len(audio_array), chunk_size):
            chunk = audio_array[i:i + chunk_size]
            sd.play(chunk, sample_rate, blocking=True)
            # RMS amplituda
            rms = float(np.sqrt(np.mean(chunk ** 2)))
            self.bridge.set_audio_amplitude(min(rms * 3.0, 1.0))
            await asyncio.sleep(0)

        self.bridge.set_audio_amplitude(0.0)

    async def _simulate_amplitude(self, duration: float = 2.0):
        """Haqiqiy audio bo'lmasa amplituda simulatsiyasi."""
        steps = int(duration / self.AMPLITUDE_INTERVAL)
        for i in range(steps):
            t = i / steps
            # Sin to'lqin simulatsiyasi
            amp = 0.3 + 0.5 * abs(math.sin(math.pi * t * 8))
            self.bridge.set_audio_amplitude(amp)
            await asyncio.sleep(self.AMPLITUDE_INTERVAL)
        self.bridge.set_audio_amplitude(0.0)

    async def _fallback_speak(self, text: str):
        """TTS mavjud bo'lmasa matnni konsolga chiqarish."""
        logger.info(f"[Voice/Fallback] 💬 {text}")
        # Amplitude simulatsiyasi UI uchun
        words = len(text.split())
        duration = max(1.5, words * 0.4)
        await self._simulate_amplitude(duration)
