from pydantic import BaseModel
from datetime import datetime
from app.schemas import UserResponse
from app.schemas.course import CourseResponse

class EnrollmentCreate(BaseModel):
    course_id: int

class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime
    user: UserResponse
    course: CourseResponse

    class Config:
        from_attributes = True
