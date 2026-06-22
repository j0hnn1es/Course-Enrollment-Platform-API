from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
# Ensure your get_redis dependency import path matches your project structure
from app.core.redis import get_redis 

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/all")
async def get_courses(
    db: Session = Depends(get_db),
    redis = Depends(get_redis) # 👈 Put it here, inside the function signature!
):
    # Now you can freely use your async Redis client instance safely
    cached_courses = await redis.get("all_courses")
    if cached_courses:
        return cached_courses
        
    # If cache miss, fetch from database and write to redis...
    return {"message": "Fetched from DB"}
