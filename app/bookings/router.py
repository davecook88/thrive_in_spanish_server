from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from app.auth.get_current_user import get_current_user
from app.db.models.availability.availability_models import (
    TeacherAvailabilityEntry,
)
from datetime import datetime

from app.db.models.user.user import User

booking_router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
    responses={404: {"description": "Not found"}},
    dependencies=[
    ]
)


async def list_bookings_params(
    from_date: str, until_date: str, limit: int = 100
):
    try:
        from_date_datetime = datetime.strptime(from_date, "%Y-%m-%d")
        until_date_datetime = datetime.strptime(until_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=422, detail="dates must be formatted YYYY-MM-DD"
        )

    return {
        "from_date": from_date_datetime,
        "until_date": until_date_datetime,
        "limit": limit,
    }


@booking_router.get(
    "/teacher-availability", response_model=List[TeacherAvailabilityEntry])
async def get_sample_data(
        current_user: User = Depends(get_current_user),
        params: Dict[str, Any] = Depends(list_bookings_params)

) -> List[TeacherAvailabilityEntry]:
    print(current_user)
    return []
