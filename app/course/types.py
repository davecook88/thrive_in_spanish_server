from typing import List, Optional
from pydantic import BaseModel

from app.db.models.course.course import CourseStudent, CourseTeacher


class CourseBase(BaseModel):
    name: str
    description: str
    difficulty: int  # Number to help order in terms of difficulty
    max_students: int = 4
    price: int
    difficulty: int
    teacher_id: int


class CourseFull(BaseModel):
    id: int
    course_teachers: List[CourseTeacher]
    course_students: List[CourseStudent]


class CourseUpdatePayload(CourseBase):
    name: Optional[str]
    description: Optional[str]
    difficulty: Optional[int]  # Number to help order in terms of difficulty
    max_students: Optional[int]
    price: Optional[int]
    difficulty: Optional[int]
