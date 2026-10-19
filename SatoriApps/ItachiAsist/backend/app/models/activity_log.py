"""
SATORI ECOSYSTEM — ItachiAssist Backend
========================================
backend/app/models/activity_log.py

SQLAlchemy ORM modeli — Satori faoliyat loglari jadvali.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class SatoriApp(Base):
    """Satori App Store reyestri."""
    __tablename__ = "satori_apps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    version: Mapped[str] = mapped_column(String(30), nullable=False)
    manifest: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ActivityLog(Base):
    """Markazlashgan faoliyat va telemetriya loglari."""
    __tablename__ = "satori_activity_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    app_slug: Mapped[str] = mapped_column(String(100), nullable=False)
    session_id: Mapped[str] = mapped_column(String(36), nullable=False)
    log_level: Mapped[str] = mapped_column(String(20), nullable=False)    # INFO, ACTION, ERROR
    category: Mapped[str] = mapped_column(String(50), nullable=False)     # OS_WINDOW, IDE_CODE
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
