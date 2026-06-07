from fastapi import FastAPI
from app.routers import auth, courses, enrollments
from app.models.base import Base
from app.core.database import engine


app = FastAPI(
    title="Course Enrollment Platform Core Platform",
    version="1.0.0",
    description="FastAPI service enforcing multi-tier constraint engines, clean schema validation layers, and role matrix mapping."
)

@app.on_event("startup")
def create_tables() -> None:
    """Create database tables at application startup, not at import time."""
    Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(enrollments.router)

@app.get("/health")
def infrastructure_health_status():
    return {"status": "operational", "engine": "FastAPI Uvicorn Execution Layer"}
