from datetime import datetime
from typing import Literal, Optional
from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import Column
from sqlmodel import Field, Relationship
from sqlalchemy.dialects.postgresql import UUID

from ...base_model import DBModel
from app.db.models.user.teacher import Teacher


AvailabilityType = Literal["available"]


class TeacherAvailability(DBModel, table=True):
    """
    Table which stores availability data for teachers.

    Each row can be a single entry or instructions for setting up
    a recurring event.
    """

    id: Optional[UUID4] = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid4),
    )

    type: str = "available"
    start: datetime
    end: datetime

    teacher_id: int = Field(foreign_key="teacher.id")
    teacher: "Teacher" = Relationship(back_populates="availability")
