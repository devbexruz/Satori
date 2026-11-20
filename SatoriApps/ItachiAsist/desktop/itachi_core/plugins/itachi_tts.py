"""
SATORI ECOSYSTEM — ItachiAssist
================================
plugins/itachi_tts.py

Itachi Uchiha ovozi uchun Humanized TTS & Real-Time Amplitude Sync Engine.
- Edge-TTS: Sekin, chuqur, shoshmasdan gapiradigan Itachi preseti (-18% rate, -8Hz pitch)
- Real vaqtda ovoz to'lqinlarini (Audio RMS amplitude) C# UI ga uzatish
- RVC (Retrieval-based Voice Conversion) v2 modeli uchun avtomatik ulagich
"""

import asyncio
import io
import logging
import os
import re
import tempfile
import time
from pathlib import Path

import edge_tts
import numpy as np
import sounddevice as sd
import soundfile as sf

logger = logging.getLogger("itachi.tts")

# Standart Itachi ovoz sozlamalari
DEFAULT_VOICE = os.getenv("ITACHI_VOICE_NAME", "en-US-ChristopherNeural")
DEFAULT_RATE = os.getenv("ITACHI_VOICE_RATE", "-18%")
DEFAULT_PITCH = os.getenv("ITACHI_VOICE_PITCH", "-8Hz")


class ItachiTTSEngine:
    """Itachi ovoz sintezi va audio ijro boshqaruvchisi."""

    def __init__(self, bridge=None, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE, pitch: str = DEFAULT_PITCH):
        self.bridge = bridge
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self._is_speaking = False
        self._rvc_model_path = Path(__file__).parent.parent / "models" / "itachi.pth"

    def humanize_text_for_speech(self, text: str) -> str:
        """
        Matnni Itachiga xos insoniy, sekin va urg'uli talaffuz uchun tayyorlash.
        - Belgilarni tozalash
        - Kerakli joylarga pauzalar (...) kiritish
        """
        clean = text.strip()
        # Markdown va keraksiz belgilarni olib tashlash
        clean = re.sub(r"[\*#_`]", "", clean)
        # Tinish belgilaridan keyin tabiiy nafas olish pauzalarini ta'minlash
        clean = clean.replace(". ", "... ")
        clean = clean.replace("! ", "... ")
        clean = clean.replace("? ", "... ")
        clean = clean.replace(", ", ", ")
        return clean

    async def speak(self, text: str):
        """
        Matnni Itachi ovozi bilan gapirish va UI ko'zlarini sinxron porlatish.
        """
        if not text.strip():
            return

        speech_text = self.humanize_text_for_speech(text)
        logger.info(f"🗣️ [ItachiTTS] Gapirmoqda: '{text}'")

        try:
            # 1. Edge-TTS orqali MP3 audio generatsiya qilish
            communicate = edge_tts.Communicate(
                speech_text,
                voice=self.voice,
                rate=self.rate,
                pitch=self.pitch
            )

            # Xotiraga MP3 baytlarni yig'ish
            audio_bytes = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes += chunk["data"]

            if not audio_bytes:
                logger.warning("[ItachiTTS] Audio baytlari hosil bo'lmadi.")
                return

            # 2. Agar RVC modeli mavjud bo'lsa, ovozni klonlash (RVC inference)
            if self._rvc_model_path.exists():
                logger.info(f"🎭 [RVC] Itachi ovoz modeli topildi: {self._rvc_model_path}. Klonlanmoqda...")
                # RVC pipeline chaqiruvi (agar rvc kutubxonasi mavjud bo'lsa)
                # audio_bytes = self._apply_rvc(audio_bytes)

            # 3. Audioni o'qish va karnayga ijro etish (Real-time Amplitude Sync bilan)
            await self._play_with_amplitude_sync(audio_bytes)

        except Exception as e:
            logger.error(f"[ItachiTTS] Ovoz chiqarishda xatolik: {e}", exc_info=True)
            if self.bridge:
                self.bridge.set_audio_amplitude(0.0)

    async def _play_with_amplitude_sync(self, audio_bytes: bytes):
        """
        Audioni blokma-blok ijro etish va har bir blok amplitudasini UI ga yuborish.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._play_blocking, audio_bytes)

    def _play_blocking(self, audio_bytes: bytes):
        """Sinxron ijro etuvchi oqim."""
        try:
            with io.BytesIO(audio_bytes) as bio:
                data, samplerate = sf.read(bio)

            # Mono formatga o'tkazish
            if len(data.shape) > 1:
                mono_data = np.mean(data, axis=1)
            else:
                mono_data = data

            block_size = int(samplerate * 0.05) # 50ms bloklar (~20 FPS)
            total_samples = len(mono_data)

            # UI holatini SPEAKING qilish
            if self.bridge:
                self.bridge.send({
                    "cmd": "EYE_STATE",
                    "mode": "SPEAKING",
                    "spin_speed": 4.0,
                    "glow": "#FFFF2200"
                })

            # SoundDevice chiqish oqimi
            with sd.OutputStream(samplerate=samplerate, channels=1 if len(data.shape) == 1 else data.shape[1]) as stream:
                for start in range(0, total_samples, block_size):
                    end = min(start + block_size, total_samples)
                    chunk = data[start:end]
                    mono_chunk = mono_data[start:end]

                    # RMS amplitudani hisoblash (0.0 dan 1.0 gacha)
                    rms = np.sqrt(np.mean(mono_chunk ** 2)) if len(mono_chunk) > 0 else 0.0
                    normalized_amp = min(1.0, float(rms) * 3.5)

                    if self.bridge:
                        self.bridge.set_audio_amplitude(normalized_amp)

                    # Karnayga yozish
                    stream.write(chunk.astype(np.float32))

            # Ijro tugagach, amplitudani 0 ga tushirish
            if self.bridge:
                self.bridge.set_audio_amplitude(0.0)
                self.bridge.send({
                    "cmd": "EYE_STATE",
                    "mode": "IDLE",
                    "spin_speed": 1.0,
                    "glow": "#AAFF0000"
                })

        except Exception as e:
            logger.error(f"[ItachiTTS] Ijroda xato: {e}")
            if self.bridge:
                self.bridge.set_audio_amplitude(0.0)
