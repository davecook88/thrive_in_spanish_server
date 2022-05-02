from fastapi import Depends
from sqlmodel import Session

from app.db.get_session import get_session
from app.db.models.user.user import User


async def get_current_user(
    token: str = "", session: Session = Depends(get_session)
):
    """
    Fake method to get a user for testing with
    """
    user = session.query(User).first()
    if not user:
        user = User.create_user(name="Karen")
    user.save(session)
    return user
