"""
SATORI ECOSYSTEM — ItachiAssist Backend
========================================
backend/app/routers/telemetry.py

Telemetry API — faoliyat loglarini qabul qilish.
POST /api/v1/telemetry/ingest
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.activity_log import ActivityLog
from app.services.pii_scrubber import scrub_dict

logger = logging.getLogger("satori.telemetry")
router = APIRouter()


# === Schemas ===

class LogItem(BaseModel):
    log_level: str = Field(..., description="INFO | ACTION | WARNING | ERROR")
    category: str = Field(..., description="OS_WINDOW | IDE_CODE | VOICE_CMD | SYSTEM")
    payload: dict[str, Any] = Field(..., description="Moslashuvchan JSONB payload")


class IngestRequest(BaseModel):
    app_slug: str = Field(..., description="Ilova identifikatori, masalan: itachi-assist")
    session_id: str = Field(..., description="UUID — joriy sessiya")
    logs: list[LogItem] = Field(..., description="Loglar ro'yxati (batch)")


class IngestResponse(BaseModel):
    received: int
    status: str = "ok"


# === Endpoint ===

@router.post("/ingest", response_model=IngestResponse)
async def ingest_logs(
    request: IngestRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Batch loglarni qabul qilish va DBga yozish.
    
    1. PII filtri orqali tozalash
    2. PostgreSQL JSONB jadvaliga yozish
    """
    if not request.logs:
        raise HTTPException(status_code=400, detail="Loglar bo'sh")

    if len(request.logs) > 1000:
        raise HTTPException(status_code=400, detail="Bir so'rovda maksimal 1000 ta log")

    records = []
    for log in request.logs:
        # Maxfiy ma'lumotlarni tozalash
        clean_payload = scrub_dict(log.payload)

        record = ActivityLog(
            app_slug=request.app_slug,
            session_id=request.session_id,
            log_level=log.log_level.upper(),
            category=log.category.upper(),
            payload=clean_payload,
        )
        records.append(record)

    db.add_all(records)
    await db.commit()

    logger.info(f"[Telemetry] {len(records)} ta log saqlandi ({request.app_slug})")
    return IngestResponse(received=len(records))


@router.get("/recent")
async def get_recent_logs(
    app_slug: str = "itachi-assist",
    minutes: int = 30,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """So'nggi N daqiqadagi loglarni olish (AI kontekst uchun)."""
    from sqlalchemy import select, and_
    from datetime import timedelta, timezone

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)

    stmt = (
        select(ActivityLog)
        .where(
            and_(
                ActivityLog.app_slug == app_slug,
                ActivityLog.created_at >= cutoff
            )
        )
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    logs = result.scalars().all()

    return {
        "count": len(logs),
        "minutes": minutes,
        "logs": [
            {
                "time": l.created_at.isoformat(),
                "level": l.log_level,
                "category": l.category,
                "payload": l.payload
            }
            for l in reversed(logs)
        ]
    }
