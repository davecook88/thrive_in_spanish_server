from typing import ClassVar, Optional
from sqlmodel import Field, Relationship
from ...base_model import DBModel
from .teacher import Teacher


class User(DBModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str
    email: str = Field(index=True)
    google_id: Optional[str] = Field(index=True, nullable=True)
    teacher: "Teacher" = Relationship()

    @property
    def is_teacher(self):
        return bool(self.teacher)

    @staticmethod
    def create_user(name: str, email: str, google_id: Optional[str] = None):
        return User(name=name, email=email, google_id=google_id)


class UserFull(User):
    id: ClassVar[int]
