from datetime import datetime
from typing import Literal, Optional
from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import Column
from sqlmodel import Field, Relationship
from sqlalchemy.dialects.postgresql import UUID

from ...base_model import DBModel
from app.db.models.user.user import User


AvailabilityType = Literal["open", "booked", "unavailable"]


class TeacherAvailabilityEntry(DBModel, table=True):
    """
    Table which stores availability data for teachers.

    Each row can be a single entry or instructions for setting up
    a recurring event.
    """

    id: Optional[UUID4] = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid4),
    )

    type: str
    from_time: datetime
    until_time: datetime

    recurring: Optional[bool] = False
    recurring_until: Optional[datetime] = None
    recurring_from: Optional[datetime] = None

    teacher_id: UUID4 = Field(foreign_key="user.id")
    teacher: "User" = Relationship(back_populates="availability")
