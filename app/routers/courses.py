from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import app.models as models
import app.schemas as schemas
from app.core.database import get_db
from app.core.security import get_current_user, RoleChecker

router = APIRouter(prefix="/courses", tags=["Course Lifecycle Directory"])

require_admin = RoleChecker(["admin"])

@router.get("/", response_model=List[schemas.CourseResponse])
def get_all_active_courses(db: Session = Depends(get_db)):
    """Public Access Point: Retrieve all active catalog elements."""
    return db.query(models.Course).filter(models.Course.is_active == True).all()

@router.get("/{course_id}", response_model=schemas.CourseResponse)
def get_course_by_id(course_id: int, db: Session = Depends(get_db)):
    """Public Access Point: Locate specific catalog reference item by ID."""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Resource Not Found: Course mapping does not exist.")
    return course

@router.post("/", response_model=schemas.CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course_in: schemas.CourseCreate, db: Session = Depends(get_db), _ = Depends(require_admin)):
    if db.query(models.Course).filter(models.Course.code == course_in.code).first():
        raise HTTPException(status_code=400, detail="Data Integrity Failure: Unique catalog alphanumeric 'code' match found.")
    
    new_course = models.Course(**course_in.model_dump())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.put("/{course_id}", response_model=schemas.CourseResponse)
def update_course_details(course_id: int, course_update: schemas.CourseUpdate, db: Session = Depends(get_db), _ = Depends(require_admin)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Resource Not Found: Targeted course reference missing.")
    
    update_data = course_update.model_dump(exclude_unset=True)
    
    if "code" in update_data:
        duplicate = db.query(models.Course).filter(models.Course.code == update_data["code"], models.Course.id != course_id).first()
        if duplicate:
            raise HTTPException(status_code=400, detail="Data Integrity Failure: Unique identifier 'code' conflict occurred.")
            
    for key, val in update_data.items():
        setattr(course, key, val)
        
    db.commit()
    db.refresh(course)
    return course
