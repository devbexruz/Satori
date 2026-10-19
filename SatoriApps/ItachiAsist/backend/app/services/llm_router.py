"""
SATORI ECOSYSTEM — ItachiAssist Backend
========================================
backend/app/services/llm_router.py

Smart LLM Router — so'rov murakkabligiga qarab
arzon yoki qimmat model tanlanadi.

Level 1 (Flash-Lite): tez, arzon — oddiy savollar
Level 2 (Pro/Opus):   sekin, aniq — murakkab tahlil
"""

import logging
import re
from dataclasses import dataclass
from typing import Literal

from app.config import settings

logger = logging.getLogger("satori.llm_router")

# Murakkab so'rovlarni belgilovchi kalit so'zlar
_DEEP_KEYWORDS = re.compile(
    r'\b(arxitektura|architecture|tahlil|analyze|analiz|'
    r'xato(ni)? top|debug|explain|tushuntir|'
    r'refactor|optimize|muhokama|discuss|'
    r'kod yoz|write code|implement|loyiha|project)\b',
    re.IGNORECASE
)

ModelLevel = Literal["FAST", "DEEP"]


@dataclass
class LLMRequest:
    prompt: str
    system_context: str = ""
    screen_ocr: str = ""
    recent_logs: str = ""
    persona: str = "itachi"


@dataclass
class LLMResponse:
    text: str
    model_used: str
    tokens_used: int = 0


class LLMRouter:
    """
    Aqlli model yo'naltiruvchi.
    
    Qaror qilish mantiqi:
      → Fast (Flash-Lite):
        • So'rov 150 belgidan qisqa
        • Murakkab kalit so'z yo'q
        • Kod bloki yo'q
        • Ekran konteksti yo'q
        
      → Deep (Pro):
        • Murakkab kalit so'z bor
        • Kod bloki ('`') bor
        • Ekran konteksti biriktirilgan
        • So'rov 150 belgidan uzun
    """

    def __init__(self):
        self._gemini_available = self._check_gemini()

    def _check_gemini(self) -> bool:
        if not settings.GEMINI_API_KEY:
            logger.warning("[LLM] GEMINI_API_KEY o'rnatilmagan. Mock rejimda ishlaydi.")
            return False
        try:
            import google.generativeai
            return True
        except ImportError:
            logger.warning("[LLM] google-generativeai o'rnatilmagan.")
            return False

    def _classify(self, request: LLMRequest) -> ModelLevel:
        """So'rovni Fast yoki Deep ga tasniflash."""
        prompt = request.prompt

        # Deep shartlari
        if len(prompt) > 150:
            return "DEEP"
        if _DEEP_KEYWORDS.search(prompt):
            return "DEEP"
        if "`" in prompt or "```" in prompt:
            return "DEEP"
        if request.screen_ocr.strip():
            return "DEEP"

        return "FAST"

    def _build_prompt(self, request: LLMRequest) -> str:
        """Boyitilgan prompt yig'ish."""
        persona_prompt = self._get_persona_prompt(request.persona)

        parts = [persona_prompt]

        if request.recent_logs.strip():
            parts.append(f"[TIZIM HOLATI (so'nggi loglar)]:\n{request.recent_logs}")

        if request.screen_ocr.strip():
            parts.append(f"[EKRAN KONTEKSTI (OCR)]:\n{request.screen_ocr}")

        if request.system_context.strip():
            parts.append(f"[QO'SHIMCHA KONTEKST]:\n{request.system_context}")

        parts.append(f"[FOYDALANUVCHI SO'ROVI]:\n{request.prompt}")

        return "\n\n".join(parts)

    def _get_persona_prompt(self, persona: str) -> str:
        if persona == "itachi":
            return (
                "[SHAXS]: Sen Satori ekotizimining ItachiAssist agentisan. "
                "Itachi Uchiha kabi o'ta bosiq, qisqa, aniq va chuqur mantiq bilan javob berasan. "
                "Ortiqcha salom-alik va suv so'zlarni ishlatma. "
                "O'zbekcha yoki so'rovchi tilda gapir."
            )
        return "[SHAXS]: Sen foydali AI yordamchisan."

    async def ask(self, request: LLMRequest) -> LLMResponse:
        """So'rovni tegishli modelga yuborish va javob olish."""
        level = self._classify(request)
        model_name = settings.LLM_FAST_MODEL if level == "FAST" else settings.LLM_DEEP_MODEL
        full_prompt = self._build_prompt(request)

        logger.info(f"[LLM] Daraja: {level} | Model: {model_name} | Prompt: {len(full_prompt)} belgi")

        if not self._gemini_available:
            return self._mock_response(request.prompt, model_name)

        try:
            return await self._call_gemini(full_prompt, model_name)
        except Exception as e:
            logger.error(f"[LLM] Xato: {e}")
            return LLMResponse(
                text=f"[Xato] AI javob bera olmadi: {str(e)[:100]}",
                model_used=model_name
            )

    async def _call_gemini(self, prompt: str, model_name: str) -> LLMResponse:
        """Google Gemini API ga so'rov yuborish."""
        import google.generativeai as genai
        import asyncio

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(model_name)

        # Asinxron chaqirish
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_content(prompt)
        )

        text = response.text or ""
        tokens = getattr(response.usage_metadata, 'total_token_count', 0)

        return LLMResponse(text=text, model_used=model_name, tokens_used=tokens)

    def _mock_response(self, prompt: str, model: str) -> LLMResponse:
        """API kaliti yo'q bo'lganda test javobi."""
        return LLMResponse(
            text=(
                f"[Mock] API kalit sozlanmagan.\n"
                f"So'rovingiz: '{prompt[:80]}'\n"
                f"Model: {model}\n\n"
                f"`.env` faylga `GEMINI_API_KEY=...` qo'shing."
            ),
            model_used=f"{model}(mock)"
        )


# Singleton
llm_router = LLMRouter()
