from datetime import datetime
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID

from pydantic import UUID4
from app.bookings.types import PostAvailabilityPayloadEvent
from app.organization.model import OrganizationModel
from ...base_model import DBModel
from typing import TYPE_CHECKING, Callable, ClassVar, List, Optional, Union
from sqlmodel import Column, Field, Relationship, Session

if TYPE_CHECKING:

    from app.db.models.course.course import CourseStudent, CourseTeacher
    from app.db.models.payment.payment import PaymentPackage


class User(DBModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str
    email: str = Field(index=True)
    google_id: Optional[str] = Field(index=True, nullable=True)
    teacher: Optional["Teacher"] = Relationship(
        back_populates="user",
    )
    student: Optional["Student"] = Relationship()
    organization_id: int = Field(foreign_key="organization.id")
    organization: OrganizationModel = Relationship()

    @staticmethod
    def create_user(
        name: str,
        organization_id: int,
        email: str,
        google_id: Optional[str] = None,
    ):

        return User(
            name=name,
            email=email,
            google_id=google_id,
            organization_id=organization_id,
        )


class UserFull(User):
    id: ClassVar[int]


class Teacher(DBModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)

    user_id: int = Field(foreign_key=User.id)
    user: User = Relationship(back_populates="teacher")
    availability: List["TeacherAvailability"] = Relationship()
    course_teacher: List["CourseTeacher"] = Relationship()

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
    course_student: List["CourseStudent"] = Relationship(
        back_populates="student"
    )
    payment_packages: List["PaymentPackage"] = Relationship(
        back_populates="student"
    )


class TeacherAvailability(DBModel, table=True):
    """
    Table which stores availability data for teachers.

    Each row can be a single entry or instructions for setting up
    a recurring event.
    """

    __tablename__: ClassVar[
        Union[str, Callable[..., str]]
    ] = "teacher_availability"

    id: Optional[UUID4] = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid4),
    )

    type: str = "available"
    start: datetime
    end: datetime
    teacher_id: Optional[int] = Field(default=None, foreign_key="teacher.id")
    teacher: Optional[Teacher] = Relationship(back_populates="availability")
    title: Optional[str] = "available"

    def update(self, payload: PostAvailabilityPayloadEvent):
        self.start = payload.start
        self.end = payload.end
        if payload.title:
            self.title = payload.title
