"""
SATORI ECOSYSTEM — ItachiAssist Backend
========================================
backend/app/main.py

FastAPI asosiy dastur.
Satori Core bilan aloqa qiluvchi API server.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import telemetry, agent
from app.config import settings
from app.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Dastur ishga tushganda va o'chganda bajariladigan kod."""
    print(f"\n🌌 Satori ItachiAssist Backend v1.0")
    print(f"📍 Manzil: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 Docs:   http://{settings.HOST}:{settings.PORT}/docs\n")
    await create_tables()
    yield
    print("\n👋 Satori Backend o'chmoqda...")


app = FastAPI(
    title="Satori ItachiAssist API",
    description="ItachiAssist AI agenti uchun backend — Telemetry va AI routing",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — Desktop client dan so'rovlar uchun
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "app://satori"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routerlarni ulash
app.include_router(telemetry.router, prefix="/api/v1/telemetry", tags=["Telemetry"])
app.include_router(agent.router,     prefix="/api/v1/agent",     tags=["AI Agent"])


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "satori-itachi-backend"}
