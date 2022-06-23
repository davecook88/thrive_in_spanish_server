from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, validator

from sqlmodel import Session
from app.auth.get_current_user import get_google_user_from_token
from app.core.config import settings
from app.db.get_session import get_session
from app.db.models.user.user import User


auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
    dependencies=[],
)


class CheckGoogleTokenBody(BaseModel):
    token: str
    email: str
    google_id: str


class CheckTokenResponse(BaseModel):
    details: User
    is_teacher: Optional[bool] = None

    @validator("is_teacher")
    def set_is_teacher(cls, val: None, values: Dict):
        user: Optional[User] = values.get("user")
        if not user:
            raise ValueError("user not found")
        return user.is_teacher


@auth_router.post(
    "/google",
)
async def check_google_token(
    body: CheckGoogleTokenBody, session: Session = Depends(get_session)
):
    try:
        user, google_info = await get_google_user_from_token(
            body.token, session
        )
        # Doublt check against submitted details
        if (
            google_info.email != body.email
            or google_info.aud != settings.GOOGLE_CLIENT_ID
        ):
            raise ValueError("Google details don't match")

        if not user:
            user = User.create_user(
                name=google_info.name,
                email=google_info.email,
                google_id=google_info.sub,
            )
            await user.save(session)
        if not user.id:
            raise ValueError("No user ID")
        return CheckTokenResponse(details=user)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google token could not be authenticated",
        )
