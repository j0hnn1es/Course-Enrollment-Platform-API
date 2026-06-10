import json
import math
from typing import Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.core import get_db, RoleChecker
from app.core.redis import get_redis, RedisError

router = APIRouter(prefix="/courses", tags=["Course Directory"])
require_admin = RoleChecker(["admin"])

@router.get("/", response_model=schemas.PaginatedCourseResponse)
async def get_all_active_courses(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    redis: Any = Depends(get_redis)
):
    # Unique page-level identification signature 
    cache_key = f"courses:page:{page}:size:{size}"
    
    # Step 1: Query the memory cache store
    try:
        cached_data = await redis.get(cache_key)
    except RedisError:
        cached_data = None

    if cached_data:
        return json.loads(cached_data)

    # Step 2: Cache miss — Retrieve from primary relational database
    query = db.query(models.Course).filter(models.Course.is_active == True)
    total_items = query.count()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    total_pages = math.ceil(total_items / size) if total_items > 0 else 1

    # Format structured schema envelope
    response_payload = {
        "total_items": total_items,
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "items": [schemas.CourseResponse.model_validate(item).model_dump() for item in items]
    }

    # Step 3: Write payload back to Redis with a 5-minute Time-To-Live (TTL)
    try:
        await redis.setex(cache_key, 300, json.dumps(response_payload))
    except RedisError:
        pass
    return response_payload

async def invalidate_courses_cache(redis: Any):
    """Helper function to clear old pagination keys when mutations happen."""
    try:
        async for key in redis.scan_iter("courses:page:*"):
            await redis.delete(key)
    except RedisError:
        pass

@router.post("/", response_model=schemas.CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_in: schemas.CourseCreate, 
    db: Session = Depends(get_db), 
    redis: aioredis.Redis = Depends(get_redis),
    _ = Depends(require_admin)
):
    if db.query(models.Course).filter(models.Course.code == course_in.code).first():
        raise HTTPException(status_code=400, detail="Catalog code already exists.")
    
    new_course = models.Course(**course_in.model_dump())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    # Invalidate old cache entries
    await invalidate_courses_cache(redis)
    return new_course

@router.put("/{course_id}", response_model=schemas.CourseResponse)
async def update_course_details(
    course_id: int, 
    course_update: schemas.CourseUpdate, 
    db: Session = Depends(get_db), 
    redis: aioredis.Redis = Depends(get_redis),
    _ = Depends(require_admin)
):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    
    update_data = course_update.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(course, key, val)
        
    db.commit()
    db.refresh(course)
    
    # Invalidate old cache entries
    await invalidate_courses_cache(redis)
    return course
