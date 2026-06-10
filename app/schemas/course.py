from pydantic import BaseModel, Field
from typing import Optional

class CourseBase(BaseModel):
    title: str
    code: str = Field(..., min_length=2, max_length=20)
    capacity: int = Field(..., gt=0, description="Capacity threshold allocation must exceed 0 seats.")
    is_active: bool = True

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

class CourseResponse(CourseBase):
    id: int
    class Config:
        from_attributes = True

class PaginatedCourseResponse(BaseModel):
    total_items: int
    page: int
    size: int
    total_pages: int
    items: list[CourseResponse]
