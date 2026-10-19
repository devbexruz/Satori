"""
SATORI ECOSYSTEM — ItachiAssist Backend
========================================
backend/app/routers/agent.py

AI Agent API — kontekstual so'rovlar.
POST /api/v1/agent/ask
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.llm_router import llm_router, LLMRequest
from app.services.pii_scrubber import scrub_text

logger = logging.getLogger("satori.agent")
router = APIRouter()


# === Schemas ===

class ScreenContext(BaseModel):
    ocr_text: str = ""
    image_base64: str | None = None  # Kelgusida vision uchun


class AskRequest(BaseModel):
    prompt: str = Field(..., description="Foydalanuvchi so'rovi")
    persona: str = Field("itachi", description="AI shaxsi: itachi | default")
    include_recent_logs: bool = Field(False, description="So'nggi loglarni kontekstga qo'shish")
    log_window_minutes: int = Field(30, ge=1, le=1440)
    screen_context: ScreenContext | None = None
    system_context: str = ""


class AskResponse(BaseModel):
    reply: str
    model_used: str
    tokens_used: int = 0


# === Endpoint ===

@router.post("/ask", response_model=AskResponse)
async def ask_agent(
    request: AskRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    AI agentga kontekstual so'rov yuborish.
    
    Jarayon:
    1. So'rovni PII dan tozalash
    2. So'nggi loglarni DB dan olish (agar kerak)
    3. LLM Router orqali model tanlash + prompt yig'ish
    4. Javob qaytarish
    """
    # 1. PII tozalash
    clean_prompt = scrub_text(request.prompt)
    clean_screen = scrub_text(request.screen_context.ocr_text if request.screen_context else "")

    # 2. So'nggi loglarni olish
    recent_logs_text = ""
    if request.include_recent_logs:
        recent_logs_text = await _get_recent_logs_text(
            db, minutes=request.log_window_minutes
        )

    # 3. LLM ga yuborish
    llm_request = LLMRequest(
        prompt=clean_prompt,
        system_context=scrub_text(request.system_context),
        screen_ocr=clean_screen,
        recent_logs=recent_logs_text,
        persona=request.persona,
    )

    response = await llm_router.ask(llm_request)

    logger.info(
        f"[Agent] Javob qaytarildi | Model: {response.model_used} | "
        f"Tokenlar: {response.tokens_used}"
    )

    return AskResponse(
        reply=response.text,
        model_used=response.model_used,
        tokens_used=response.tokens_used,
    )


async def _get_recent_logs_text(db: AsyncSession, minutes: int) -> str:
    """So'nggi loglarni LLM uchun matn formatida olish."""
    from sqlalchemy import select
    from datetime import datetime, timedelta, timezone
    from app.models.activity_log import ActivityLog
    import json

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)

    stmt = (
        select(ActivityLog)
        .where(ActivityLog.created_at >= cutoff)
        .order_by(ActivityLog.created_at.desc())
        .limit(50)
    )

    result = await db.execute(stmt)
    logs = result.scalars().all()

    if not logs:
        return ""

    lines = []
    for log in reversed(logs):
        time_str = log.created_at.strftime("%H:%M:%S")
        payload_str = json.dumps(log.payload, ensure_ascii=False, separators=(",", ":"))
        lines.append(f"[{time_str}] [{log.log_level}] {log.category}: {payload_str}")

    return "\n".join(lines)
