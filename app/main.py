from typing import Any
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.routers import auth, courses, enrollments
from app.models.base import Base
from app.core.database import get_db, engine # Ensure this matches your core imports
from app.core.redis import get_redis, RedisError
from app.middleware.cors import setup_cors_middleware
from app.middleware.logging import ResponseTimingMiddleware

# 1. Use Lifespan for Safe Database Table Generation on Startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events clean and asynchronously."""
    # Create database tables safely at application startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown clean up logic can go here if needed

app = FastAPI(
    title="Course Enrollment Platform Core Platform",
    version="1.0.0",
    description="FastAPI service enforcing multi-tier constraint engines, clean schema validation layers, and role matrix mapping.",
    lifespan=lifespan
)

# 2. Setup Middleware Layout
setup_cors_middleware(app)
app.add_middleware(ResponseTimingMiddleware)

# 3. Router Submodule Attachments
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(enrollments.router)

# 4. Correctly Placed Root Route
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Course Enrollment Platform API!",
        "documentation": "/docs",
        "status": "operational"
    }

# 5. Lightweight Container Health Check (Targeted by Docker / Render)
@app.get("/health")
def shallow_health_status():
    """Simple 200 OK ping to keep the cloud container runner active."""
    return {"status": "operational", "engine": "FastAPI Uvicorn Container Layer"}

# 6. Deep Subsystem Health Check (For Internal Monitoring)
@app.get("/health/deep")
async def deep_infrastructure_health_status(
    db: Session = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    """Checks the live connectivity status of Postgres and Redis."""
    health = {
        "status": "operational",
        "engine": "FastAPI Uvicorn Execution Layer",
        "database": "unavailable",
        "cache": "unavailable",
    }

    try:
        db.execute(text("SELECT 1"))
        health["database"] = "available"
    except Exception:
        health["database"] = "unavailable"

    try:
        if hasattr(redis, "ping"):
            await redis.ping()
            health["cache"] = "available"
    except RedisError:
        health["cache"] = "unavailable"
    except Exception:
        health["cache"] = "unavailable"

    return health
