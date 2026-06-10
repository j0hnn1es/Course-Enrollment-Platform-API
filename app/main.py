from typing import Any

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.routers import auth, courses, enrollments
from app.models.base import Base
from app.core import get_db
from app.core.database import engine
from app.core.redis import get_redis, RedisError
from app.middleware.cors import setup_cors_middleware
from app.middleware.logging import ResponseTimingMiddleware


app = FastAPI(
    title="Course Enrollment Platform Core Platform",
    version="1.0.0",
    description="FastAPI service enforcing multi-tier constraint engines, clean schema validation layers, and role matrix mapping."
)

# Setup middleware
setup_cors_middleware(app)
app.add_middleware(ResponseTimingMiddleware)

@app.on_event("startup")
def create_tables() -> None:
    """Create database tables at application startup, not at import time."""
    Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(enrollments.router)

@app.get("/health")
async def infrastructure_health_status(
    db: Session = Depends(get_db),
    redis: Any = Depends(get_redis),
):
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
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.routers import auth, courses, enrollments
# from app.middleware.logging import ResponseTimingMiddleware
# from app.core import engine
# from app.models.base import Base

# # Automatically create local schema states initially if running outside migration sequences
# Base.metadata.create_all(bind=engine)

# app = FastAPI(
#     title="Course Enrollment Platform Core Platform",
#     version="2.0.0",
#     description="Containerized system utilizing security middleware and performance timing tracking metrics."
# )

# # --- 1. CORE MIDDLEWARE MOUNTING LAYER ---

# # Enforce Cross-Origin Resource Sharing rules to prevent browser scripting hacks
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Adjust this to precise production domain arrays on live web hosts
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Attach processing execution metrics tracker
# app.add_middleware(ResponseTimingMiddleware)


# # --- 2. ROUTER SUBMODULE ATTACHMENTS ---
# app.include_router(auth.router)
# app.include_router(courses.router)
# app.include_router(enrollments.router)

# @app.get("/health")
# def infrastructure_health_status():
#     return {"status": "operational", "engine": "FastAPI Uvicorn Container Layer"}
