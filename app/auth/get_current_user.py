from typing import Any, Mapping, Optional, Tuple, Union
from fastapi import Depends, Header
from pydantic import BaseModel
from sqlmodel import Session
from google.oauth2 import id_token
from google.auth.transport import requests

from app.core.config import settings
from app.db.models.user.user import User
from app.db.get_session import get_session


class DecodedGoogleResponse(BaseModel):
    iss: Optional[str] = None
    azp: Optional[str] = None
    aud: Optional[str] = None
    sub: str
    hd: Optional[str] = None
    email: str
    email_verified: Optional[str] = None
    at_hash: Optional[str] = None
    name: str
    picture: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    locale: Optional[str] = None
    iat: Optional[str] = None
    exp: Optional[str] = None
    jti: Optional[str] = None
    alg: Optional[str] = None
    kid: Optional[str] = None
    typ: Optional[str] = None


async def get_google_user_from_token(
    token: str, session: Session
) -> Tuple[Union[User, None], DecodedGoogleResponse]:
    """
    Receives a google id_token and gets the matching user
    from the database
    """
    idinfo: Mapping[str, Any] = id_token.verify_oauth2_token(
        token, requests.Request(), settings.GOOGLE_CLIENT_ID
    )
    google_info = DecodedGoogleResponse(**idinfo)
    user = session.query(User).filter(User.google_id == google_info.sub).first()
    return user, google_info


async def get_current_user(
    authorization: str = Header(), session: Session = Depends(get_session)
):
    token = authorization.replace("Bearer ", "")
    idinfo: Mapping[str, Any] = id_token.verify_oauth2_token(
        token, requests.Request(), settings.GOOGLE_CLIENT_ID
    )
    google_info = DecodedGoogleResponse(**idinfo)
    user = session.query(User).filter(User.google_id == google_info.sub).first()
    return user
