from typing import Callable, ClassVar, Optional, Union

from sqlmodel import Field
from app.db.base_model import DBModel


class StudyLevel(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "study_level"
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str
    difficulty: int  # Number to help order in terms of difficulty


class StudyLevelUnit(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "study_level_unit"
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str
    position: int  # Position in course
