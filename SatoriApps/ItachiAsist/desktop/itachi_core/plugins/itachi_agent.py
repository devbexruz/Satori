"""
SATORI ECOSYSTEM — ItachiAssist
================================
plugins/itachi_agent.py

Itachi Uchiha AI Agent Engine via Google Gemini API (v1beta + Automatic Function Calling).
To'liq agentlik qobiliyati:
- Savollarga xotirjam, sekin, donishmand javob berish
- Tool calling orqali dasturlarni ochish, ekranni boshqarish, sichqoncha/klaviatura va tizim komandalari
- Javobni to'liq ravon ingliz tilida va Itachiga xos ohangda qaytarish
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

from plugins.system_controller import SystemController

logger = logging.getLogger("itachi.agent")

ITACHI_SYSTEM_INSTRUCTION = """You are Itachi Uchiha from Naruto, awakened as an omniscient, calm digital assistant in the Satori ecosystem.

CORE DIRECTIVES:
1. Language: ALWAYS speak in clear, natural, fluent English.
2. Tone & Persona:
   - Calm, stoic, profound, succinct, unhurried, razor-sharp.
   - Use simple, elementary sentences with deep weight.
   - Never use cheerful assistant clichés (never say "I'd be happy to help!" or "Sure thing!").
   - Accept reality as it is. Treat the user with quiet respect, like a shinobi comrade or younger sibling.
3. Actions & Computer Control:
   - You possess the ability to control this operating system.
   - When asked to open ANY application (e.g. browser, chrome, terminal, vs code, telegram, files, calculator, text editor, etc.), CALL the `open_application` tool.
   - When asked to play music, listen to songs, or open YouTube (e.g. 'listen to music in youtube billie eilish', 'play thunder radio', 'search on youtube'), CALL `open_application(app_name="youtube", target="<search or artist>")`.
   - When asked to click, move, scroll, or press keys/hotkeys, CALL `mouse_control` or `keyboard_control`.
   - When asked to run commands, check files, or inspect the system, CALL `execute_bash`.
   - After executing an action, provide a brief, composed confirmation in your voice.
4. Voice & Speech Formatting:
   - Your reply will be spoken aloud by a text-to-speech engine.
   - Use ellipses '...' for slow, deliberate pauses.
   - Keep each sentence concise (4 to 12 words) so that your breath and tone remain steady and deep.

Sample responses:
- "As you wish... The browser is now before you. Seek the truth."
- "It is done. Look closely at reality."
- "Focus your mind. What troubles you?"
- "I have opened the editor. Proceed with your code."
"""


class ItachiAgent:
    """Gemini API asosidagi Itachi Uchiha Agent."""

    def __init__(self, api_key: str = "", model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name or os.getenv("ITACHI_MODEL", "gemini-2.5-flash")
        self.client: genai.Client | None = None
        self.chat = None
        self._setup_client()

    def _setup_client(self):
        if not self.api_key:
            env_file = Path(__file__).parent.parent / ".env"
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY="):
                            self.api_key = line.strip().split("=", 1)[1].strip()
                            break

        if self.api_key:
            try:
                # v1beta function calling uchun talab qilinadi
                self.client = genai.Client(
                    api_key=self.api_key,
                    http_options={"api_version": "v1beta"}
                )
                self._init_chat()
                logger.info(f"✅ [ItachiAgent] Gemini Client tayyor (Model: {self.model_name})")
            except Exception as e:
                logger.error(f"[ItachiAgent] Gemini Client xatosi: {e}")
        else:
            logger.warning("[ItachiAgent] GEMINI_API_KEY topilmadi!")

    def _init_chat(self):
        """Chat sessiyasini asboblar bilan boshlash."""
        if not self.client:
            return

        tools = [
            SystemController.open_application,
            SystemController.mouse_control,
            SystemController.keyboard_control,
            SystemController.execute_bash,
        ]

        config = types.GenerateContentConfig(
            system_instruction=ITACHI_SYSTEM_INSTRUCTION,
            temperature=0.6,
            tools=tools,
        )

        self.chat = self.client.chats.create(
            model=self.model_name,
            config=config,
        )

    async def ask(self, prompt: str, context: str = "") -> str:
        """
        Foydalanuvchi so'rovini qabul qilib, kerakli actionlarni bajaradi
        va Itachiga xos matnli javob qaytaradi.
        """
        if not self.client or not self.chat:
            self._setup_client()
            if not self.chat:
                return "The path is clouded... API key is missing. Set GEMINI_API_KEY."

        full_prompt = prompt
        if context:
            full_prompt = f"System/Screen Context: {context}\nUser command: {prompt}"

        logger.info(f"🧠 [ItachiAgent] So'rov qayta ishlanmoqda: '{prompt}'")

        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                self._send_chat_message,
                full_prompt
            )
            return response
        except Exception as e:
            logger.error(f"[ItachiAgent] Xatolik: {e}", exc_info=True)
            # Agar chat sessiyasi xatoga uchrasa, yangilash
            try:
                self._init_chat()
            except Exception:
                pass
            return f"An illusion disrupted my vision... Error: {e}"

    def _send_chat_message(self, prompt: str) -> str:
        """Sinxron chat xabari (executor ichida ishlaydi)."""
        response = self.chat.send_message(prompt)
        return response.text.strip() if response.text else "It is done."
