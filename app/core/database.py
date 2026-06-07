from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings  # Updated Import Path

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Yields a database session instance per HTTP Request Context lifecycle."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
