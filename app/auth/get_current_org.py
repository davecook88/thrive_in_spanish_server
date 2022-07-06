from fastapi import Depends
from sqlmodel import Session

from app.db.get_session import get_session
from app.organization.model import OrganizationModel


def get_current_organization(session: Session = Depends(get_session)):
    return OrganizationModel.get_default_organization(session)
