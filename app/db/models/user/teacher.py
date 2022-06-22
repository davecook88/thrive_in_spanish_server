from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship
from app.db.base_model import DBModel


from app.db.models.user.user import User

if TYPE_CHECKING:
    from ..availability.availability_models import TeacherAvailability


class Teacher(DBModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user: User = Relationship(back_populates=None)
    user_id: int = Field(foreign_key="user.id")
    availability: List["TeacherAvailability"] = Relationship()
