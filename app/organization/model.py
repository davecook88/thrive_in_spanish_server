from typing import ClassVar, Optional, Union

from pydantic import CallableError
from sqlmodel import Field, Session
from app.db.base_model import DBModel
from app.core.config import settings


class OrganizationModel(DBModel, table=True):
    __tablename__: ClassVar[
        Union[str, CallableError[..., str]]  # type: ignore
    ] = "organization"
    id: Optional[int] = Field(primary_key=True, default=None)

    @staticmethod
    def get_default_organization(session: Session) -> "OrganizationModelFull":
        org = session.get(
            OrganizationModelFull, settings.DEFAULT_ORGANIZATION_ID
        )
        if org:
            return org
        org = OrganizationModel(id=settings.DEFAULT_ORGANIZATION_ID)
        session.add(org)
        session.commit()
        org = session.get(OrganizationModelFull, org.id)
        if not org:
            raise Exception("Error getting default organization")
        return org


class OrganizationModelFull(OrganizationModel):
    id: ClassVar[int]
