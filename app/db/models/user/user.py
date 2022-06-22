from typing import Optional
from sqlmodel import Field
from ...base_model import DBModel


class User(DBModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str
    email: str = Field(index=True)
    google_id: Optional[str] = Field(index=True, nullable=True)

    @staticmethod
    def create_user(name: str, email: str, google_id: Optional[str] = None):
        return User(name=name, email=email, google_id=google_id)
