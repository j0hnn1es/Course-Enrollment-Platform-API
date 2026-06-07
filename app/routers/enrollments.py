from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import app.models as models
import app.schemas as schemas
from app.core.database import get_db
from app.core.security import get_current_user, RoleChecker

router = APIRouter(prefix="/enrollments", tags=["Enrollment Transaction Engine"])

@router.post("/", response_model=schemas.EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_student(enroll_in: schemas.EnrollmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Functional Rule: Verify account explicitly retains 'student' role
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Operational Guard Exception: Only student role context can self-enroll.")

    course = db.query(models.Course).filter(models.Course.id == enroll_in.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Reference Lookup Error: Course registry target missing.")

    # Functional Rule: Block transaction if course state is marked inactive
    if not course.is_active:
        raise HTTPException(status_code=400, detail="Operational Integrity Failure: Target catalog entity is currently inactive.")

    # Functional Rule: Enforce matching single unique registration block constraint
    already_enrolled = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == current_user.id,
        models.Enrollment.course_id == course.id
    ).first()
    if already_enrolled:
        raise HTTPException(status_code=400, detail="Duplicate Request: Already registered in this course module context.")

    # Functional Rule: Check seat availability limits
    allocated_seats = db.query(models.Enrollment).filter(models.Enrollment.course_id == course.id).count()
    if allocated_seats >= course.capacity:
        raise HTTPException(status_code=400, detail="Capacity Conflict Error: Target class listing capacity full.")

    new_enrollment = models.Enrollment(user_id=current_user.id, course_id=course.id)
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    return new_enrollment

@router.delete("/cancel/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def deregister_student_self(course_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == current_user.id,
        models.Enrollment.course_id == course_id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Context Exception: No matching active enrollment to remove.")
        
    db.delete(enrollment)
    db.commit()

# --- ADMINISTRATIVE OVERSIGHT PORTS ---
require_admin = RoleChecker(["admin"])

@router.get("/admin/all", response_model=List[schemas.EnrollmentResponse])
def admin_view_all_enrollments(db: Session = Depends(get_db), _ = Depends(require_admin)):
    return db.query(models.Enrollment).all()

@router.get("/admin/course/{course_id}", response_model=List[schemas.EnrollmentResponse])
def admin_view_course_enrollments(course_id: int, db: Session = Depends(get_db), _ = Depends(require_admin)):
    return db.query(models.Enrollment).filter(models.Enrollment.course_id == course_id).all()

@router.delete("/admin/remove/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_force_remove_student(enrollment_id: int, db: Session = Depends(get_db), _ = Depends(require_admin)):
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Context Exception: Targeted enrollment entry was not found.")
    db.delete(enrollment)
    db.commit()
