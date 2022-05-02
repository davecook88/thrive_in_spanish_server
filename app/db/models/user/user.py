from typing import Optional
from uuid import uuid4
from pydantic import UUID4
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Column
from sqlmodel import Field
from ...base_model import DBModel


class User(DBModel, table=True):
    id: Optional[UUID4] = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid4),
    )
    name: str

    @staticmethod
    def create_user(name: str):
        return User(
            name=name,
            id=uuid4(),
        )
