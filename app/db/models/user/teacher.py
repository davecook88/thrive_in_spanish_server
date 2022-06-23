from typing import TYPE_CHECKING, Callable, ClassVar, List, Optional, Union
from sqlmodel import Field, Relationship, Session
from app.db.base_model import DBModel


if TYPE_CHECKING:
    from ..availability.availability_models import TeacherAvailability
    from app.db.models.user.user import User


class Teacher(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "teacher"
    id: Optional[int] = Field(primary_key=True, default=None)
    user: "User" = Relationship(back_populates="teacher")
    user_id: int = Field(foreign_key="user.id", index=True)
    availability: List["TeacherAvailability"] = Relationship()

    @classmethod
    def get_teacher_by_user_id(cls, session: Session, user_id: int):
        teacher = session.query(cls).filter(cls.user_id == user_id).first()
        if not teacher:
            raise ValueError(f"No teacher found for user {user_id}")
        return teacher
