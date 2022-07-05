from ...base_model import DBModel
from typing import TYPE_CHECKING, ClassVar, List, Optional
from sqlmodel import Field, Relationship, Session

if TYPE_CHECKING:
    from app.db.models.availability.availability_models import (
        TeacherAvailability,
    )
    from app.db.models.course.course import CourseStudent


class User(DBModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str
    email: str = Field(index=True)
    google_id: Optional[str] = Field(index=True, nullable=True)
    teacher: Optional["Teacher"] = Relationship(
        back_populates="user",
    )

    @staticmethod
    def create_user(name: str, email: str, google_id: Optional[str] = None):
        return User(name=name, email=email, google_id=google_id)


class UserFull(User):
    id: ClassVar[int]


class Teacher(DBModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)

    user_id: int = Field(foreign_key=User.id)
    user: User = Relationship(back_populates="teacher")
    availability: List["TeacherAvailability"] = Relationship(
        back_populates="teacher"
    )

    @classmethod
    def get_teacher_by_user_id(cls, session: Session, user_id: int):
        teacher = session.query(cls).filter(cls.user_id == user_id).first()
        if not teacher:
            raise ValueError(f"No teacher found for user {user_id}")
        return teacher


class Student(DBModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)

    user_id: int = Field(foreign_key=User.id)
    user: User = Relationship(back_populates="student")
    course_students: "CourseStudent" = Relationship(back_populates="student")
