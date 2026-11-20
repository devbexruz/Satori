"""
SATORI ECOSYSTEM — ItachiAssist
================================
plugins/voice_listener.py

Real-Time Sliding Window Wake Word Detection & Continuous Audio Pipeline.
Xususiyatlari:
1. Haqiqiy Real-Time Tahlil (Sliding Window):
   - Nutq to'xtashini kutmasdan, nutq boshlanishi bilan 0.5 soniyalik oraliqda
     sirg'aluvchi audio oynasini (sliding window) tahlil qiladi.
   - "Hey Itachi" yoki "Itashi" aytilishi bilanoq BIR LAHZADA ko'zlari qizil yonadi!
2. Uzluksiz Audio Segmentatsiyasi:
   - Wake word aniqlangan paytda audio to'xtatilmaydi, keyingi aytilgan butun jumla
     ("i want to listen to music in youtube billie eilish") bilan birlashtirilib tahlil qilinadi.
3. Faol Suhbat Oynasi (15 soniya):
   - Itachi uyg'ongandan so'ng 15 soniya davomida keyingi savollar uchun "Hey Itachi"ni
     qayta-qayta takrorlash shart emas, to'g'ridan-to'g'ri buyruq berish mumkin.
4. Keng Fonetik Qamrov:
   - "itachi", "itashi", "hey itachi", "hey itashi", "hitachi", "harry", "aytachi" va h.k.
"""

import asyncio
import collections
import io
import logging
import re
import threading
import time
from typing import Any

import numpy as np
import sounddevice as sd
import speech_recognition as sr

logger = logging.getLogger("itachi.voice_listener")

WAKE_KEYWORDS = [
    "itachi", "hey itachi", "ey itachi", "hay itachi",
    "itashi", "hey itashi", "ey itashi", "hay itashi",
    "hitachi", "hey hitachi", "hi itachi", "hay hitachi",
    "aytachi", "aytashi", "itach", "itash",
    "eatachi", "itachy", "itachee", "itashe", "itashee",
    "tachi", "hi tachi", "hey tachi", "tashi", "hey tashi",
    "harry",  # Google STT tez-tez "itachi"ni "harry" deb transkripsiya qiladi
    "итачи", "хей итачи", "эй итачи", "хитачи", "иташи", "хей иташи",
]


class VoiceListenerPlugin:
    """Real-Time Sliding Window Wake Word & Audio Pipeline."""

    def __init__(self, bus, bridge):
        self.bus = bus
        self.bridge = bridge
        self._running = False
        self._recognizer = sr.Recognizer()
        self._sample_rate = 16000
        self._block_size = 1024

        # Real-time Sliding Window buferlari (~1.2 soniya = 18 blok)
        self._sliding_buffer = collections.deque(maxlen=20)
        self._pre_buffer = collections.deque(maxlen=6)  # 0.4s pre-speech
        self._current_utterance = []
        self._lock = threading.Lock()

        # VAD & Holat
        self._is_speaking = False
        self._silence_start = None
        self._speech_start_time = None
        self._ambient_rms = 1200.0

        # Realtime Wake Word nazorati
        self._wake_triggered = False
        self._wake_check_busy = False
        self._blocks_since_last_check = 0
        self._awake_until = 0.0  # Suhbat faol bo'lgan vaqt chegarasi

        # Qo'lda boshqaruv (Push-to-Talk)
        self._manual_recording = False
        self._was_manual = False

        self._stream = None
        self._worker_thread = None

        # UI mikrafon tugmasi hodisasi
        self.bus.subscribe("MIC_BUTTON_TOGGLED", self._on_mic_button)

    def start(self):
        """Mikrofonni ishga tushirish."""
        self._running = True
        try:
            self._stream = sd.InputStream(
                samplerate=self._sample_rate,
                channels=1,
                dtype="int16",
                callback=self._audio_callback,
                blocksize=self._block_size
            )
            self._stream.start()
            logger.info("🎙️ [VoiceListener] Real-time audio tahlil faollashdi. 'Hey Itachi' / 'Itashi' kutilmoqda...")
        except Exception as e:
            logger.warning(f"⚠️ [VoiceListener] Mikrofon xatosi: {e}")

    def stop(self):
        """To'xtatish."""
        self._running = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass

    def _on_mic_button(self, data: Any = None):
        """UI mikrafon tugmasi bosilganda."""
        logger.info("🎙️ [VoiceListener] UI Mikrofon bosildi — majburiy tinglash")
        self._was_manual = True
        self._wake_triggered = True
        self._awake_until = time.time() + 15.0
        self._is_speaking = True
        self._speech_start_time = time.time()
        self._silence_start = None
        with self._lock:
            self._current_utterance.clear()
        self.bridge.trigger_wake_animation()
        self.bridge.send_chat_reply("Listening... Speak your command.", typing_effect=False)

    def _audio_callback(self, indata, frames, time_info, status):
        """Har 64ms da mikrofon blokini tahlil qilish."""
        if not self._running:
            return

        data = indata.flatten()
        rms = float(np.sqrt(np.mean(data.astype(np.float32) ** 2))) if len(data) > 0 else 0.0

        # Shovqin polini adaptiv yangilash
        if not self._is_speaking:
            self._ambient_rms = self._ambient_rms * 0.96 + rms * 0.04
            with self._lock:
                self._pre_buffer.append(data.copy())

        # Dinamik chegara
        threshold = max(self._ambient_rms * 1.5, self._ambient_rms + 550.0)

        # Sliding window buferiga har doim yozish
        self._sliding_buffer.append(data.copy())

        # Gapirish aniqlanganda
        if rms > threshold:
            if not self._is_speaking:
                self._is_speaking = True
                self._speech_start_time = time.time()
                self._blocks_since_last_check = 0
                with self._lock:
                    self._current_utterance.extend(list(self._pre_buffer))
                    self._pre_buffer.clear()
                logger.debug(f"🎙️ [Voice] Nutq boshlandi (RMS: {rms:.0f} > {threshold:.0f})")

            self._silence_start = None
            with self._lock:
                self._current_utterance.append(data.copy())

            # ─────────────────────────────────────────────────────────────────
            # REALTIME SLIDING WINDOW TEKSHIRUV:
            # Nutq davom etayotganda to'xtashni KUTMASDAN, har ~0.5 soniyada
            # (har 8 ta blokda) sliding window orqali wake word qidiriladi!
            # ─────────────────────────────────────────────────────────────────
            self._blocks_since_last_check += 1
            if not self._wake_triggered and self._blocks_since_last_check >= 8:
                self._blocks_since_last_check = 0
                if len(self._sliding_buffer) >= 12:
                    window_data = np.concatenate(list(self._sliding_buffer))
                    self._trigger_async_wake_check(window_data)

            # Maksimal vaqt chegarasi (7 soniya)
            if self._speech_start_time and (time.time() - self._speech_start_time > 7.0):
                self._finalize_speech()

        elif self._is_speaking:
            # Sukunat boshlandi
            now = time.time()
            if self._silence_start is None:
                self._silence_start = now
            with self._lock:
                self._current_utterance.append(data.copy())

            # Sukunat 0.65 soniya davom etsa, ibora yakunlandi
            if now - self._silence_start > 0.65:
                self._finalize_speech()

    def _trigger_async_wake_check(self, pcm_data: np.ndarray):
        """Fon threadida real vaqtda sliding window dan wake word qidirish."""
        if self._wake_check_busy or self._wake_triggered:
            return

        def _worker():
            self._wake_check_busy = True
            try:
                raw_bytes = pcm_data.tobytes()
                audio_data = sr.AudioData(raw_bytes, self._sample_rate, 2)
                text = ""
                try:
                    text = self._recognizer.recognize_google(audio_data, language="en-US").lower()
                except Exception:
                    pass

                if text:
                    logger.debug(f"⚡ [Realtime Scan] '{text}'")
                    for kw in WAKE_KEYWORDS:
                        if kw in text:
                            # BIR LAHZADA WAKE EFFECT! Nutq tugashini kutmaydi!
                            logger.info(f"🔥 [Realtime Wake] '{kw}' darhol aniqlandi! Itachining ko'zlari yondi!")
                            self._wake_triggered = True
                            self._awake_until = time.time() + 15.0
                            self.bridge.trigger_wake_animation()
                            self.bus.emit_sync("WAKE_WORD_DETECTED", {"keyword": kw, "realtime": True})
                            break
            finally:
                self._wake_check_busy = False

        threading.Thread(target=_worker, daemon=True).start()

    def _finalize_speech(self):
        """Nutq tugaganda butun to'plangan iborani yakuniy tahlil qilish."""
        self._is_speaking = False
        self._silence_start = None
        self._speech_start_time = None

        with self._lock:
            if len(self._current_utterance) < 8:
                self._current_utterance.clear()
                return
            full_data = np.concatenate(self._current_utterance)
            self._current_utterance.clear()

        # Fon oqimida yakuniy natijani olish
        threading.Thread(target=self._process_final_utterance, args=(full_data,), daemon=True).start()

    def _process_final_utterance(self, pcm_data: np.ndarray):
        """Butun gapirilgan iborani aniqlash va buyruqni AI ga uzatish."""
        try:
            raw_bytes = pcm_data.tobytes()
            audio_data = sr.AudioData(raw_bytes, self._sample_rate, 2)

            text = ""
            try:
                text = self._recognizer.recognize_google(audio_data, language="en-US").lower()
            except sr.UnknownValueError:
                pass
            except Exception as e:
                logger.debug(f"[Voice] Google en-US: {e}")

            if not text:
                try:
                    text = self._recognizer.recognize_google(audio_data, language="uz-UZ").lower()
                except Exception:
                    pass

            if not text:
                return

            logger.info(f"🎙️ [Voice] To'liq eshitilgan jumlalar: '{text}'")

            # 1. Wake word bor-yo'qligini tekshirish
            matched_kw = None
            for kw in WAKE_KEYWORDS:
                if kw in text:
                    matched_kw = kw
                    break

            is_already_awake = time.time() < self._awake_until

            # Agar wake word aytilgan bo'lsa yoki Itachi hozir faol uyg'oq bo'lsa:
            if matched_kw or is_already_awake or self._was_manual:
                self._was_manual = False

                # Agar wake word real-time da hali chaqnagan bo'lmasa, hozir chaqnatish
                if not self._wake_triggered:
                    self.bridge.trigger_wake_animation()

                self._wake_triggered = False
                self._awake_until = time.time() + 15.0  # Yana 15 soniya faol turish

                # Buyruq matnini tozalash (masalan: "hey itachi i want to listen..." -> "i want to listen...")
                prompt = text
                if matched_kw:
                    prompt = prompt.replace(matched_kw, "").strip()
                prompt = re.sub(r"^[,\.\?!:\s]+", "", prompt).strip()

                if len(prompt) > 2:
                    logger.info(f"💡 [Voice] Itachiga buyruq yuborilmoqda: '{prompt}'")
                    self.bus.emit_sync("USER_TEXT_SUBMIT", {
                        "text": prompt,
                        "include_screen": False
                    })
                else:
                    # Faqat "Hey Itachi" yoki "Itashi" deyilgan bo'lsa:
                    logger.info("🔥 [Voice] Faqat chaqiruv — Itachi javob beradi")
                    self.bus.emit_sync("USER_TEXT_SUBMIT", {
                        "text": "Hello Itachi, I am here.",
                        "include_screen": False
                    })
            else:
                self._wake_triggered = False

        except Exception as e:
            logger.error(f"[Voice] Yakuniy tahlilda xato: {e}")
            self._wake_triggered = False
