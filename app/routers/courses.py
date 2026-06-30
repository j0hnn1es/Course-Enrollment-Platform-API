import json
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import RoleChecker # 👈 Ensure this import is active

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("/all")
async def get_courses(
    db: Session = Depends(get_db),
    redis = Depends(get_redis) 
):
    # Try reading data from your cache engine layer first
    try:
        cached_courses = await redis.get("all_courses")
        if cached_courses:
            return json.loads(cached_courses)
    except Exception:
        pass
        
    # Fetch from relational database if cache is empty
    courses = db.query(models.Course).all()
    return courses


# --- 2. THE NEWLY ADDED ADMIN CREATE ENDPOINT ---
@router.post(
    "/create", 
    response_model=schemas.CourseResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(["admin"]))] # 👈 Blocks non-admins immediately
)
async def create_course(
    payload: schemas.CourseCreate,
    db: Session = Depends(get_db),
    redis: Any = Depends(get_redis)
):
    
    # 1. Enforce unique index data mappings across course codes 
    existing_code = db.query(models.Course).filter(models.Course.code == payload.code).first()
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Constraint Error: A course with this specific code sequence already exists."
        )

    # 2. Map schema to database model parameters and commit row
    new_course = models.Course(**payload.model_dump())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    # 3. Clear the Redis cache to ensure subsequent GET requests reflect the new state
    try:
        await redis.delete("all_courses")
    except Exception:
        pass

    return new_course
