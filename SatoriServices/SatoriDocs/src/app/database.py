import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("uvicorn")

Base = declarative_base()

# Attempt connection to configured PostgreSQL database.
# Fallback to local SQLite if connection fails (e.g. Docker container not running locally).
try:
    if settings.DATABASE_URL.startswith("postgresql"):
        # Create a temporary engine to test connectivity quickly
        test_engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True
        )
        # Try a dummy connection
        with test_engine.connect() as conn:
            pass
        engine = test_engine
        logger.info("Successfully connected to PostgreSQL database.")
    else:
        engine = create_engine(settings.DATABASE_URL)
except Exception as e:
    logger.warning(
        f"Could not connect to PostgreSQL database at {settings.DATABASE_URL}. "
        f"Error: {e}. Falling back to SQLite for local development."
    )
    # SQLite connection configuration
    engine = create_engine(
        "sqlite:///satori_docs.db",
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI dependency that provides a transactional database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
