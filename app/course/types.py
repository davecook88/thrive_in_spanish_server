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
    teacher_ids: List[int]
    student_ids: List[int] | None = None


class CourseFull(BaseModel):
    id: int
    course_teachers: List[CourseTeacher]
    course_students: Optional[List[CourseStudent]] = None


class CourseUpdatePayload(CourseBase):
    name: Optional[str]
    description: Optional[str]
    difficulty: Optional[int]  # Number to help order in terms of difficulty
    max_students: Optional[int]
    price: Optional[int]
    difficulty: Optional[int]
