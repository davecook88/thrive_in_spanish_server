from typing import List
from sqlalchemy import and_
from app.auth.get_current_user import get_current_user
from app.bookings.types import (
    PostAvailabilityPayload,
    PostAvailabilityPayloadEvent,
)
from app.bookings.utils import clear_availability
from app.db.get_session import get_session
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, col, select
from app.db.models.user.user import (
    TeacherAvailability,
)
from datetime import datetime

from app.db.models.user.user import User, Teacher
from app.utils.params import ListAPIParams

booking_router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
    responses={404: {"description": "Not found"}},
    dependencies=[],
)


class ListBookingsParams(ListAPIParams):
    from_date: datetime
    until_date: datetime


async def list_bookings_params(
    from_date: datetime, until_date: datetime, limit: int = 100, page: int = 0
):
    try:
        params = ListBookingsParams(
            from_date=from_date, until_date=until_date, limit=limit, page=page
        )
        return params
    except Exception as e:
        print(e)


@booking_router.get(
    "/teacher-availability", response_model=List[TeacherAvailability]
)
async def get_availiability(
    current_user: User = Depends(get_current_user),
    params: ListBookingsParams = Depends(list_bookings_params),
    session: Session = Depends(get_session),
) -> List[TeacherAvailability]:
    statement = (
        select(TeacherAvailability)
        .join(Teacher)
        .join(User)
        .where(
            and_(
                col(User.id) == current_user.id,
                col(TeacherAvailability.end) < params.until_date,
                col(TeacherAvailability.start) > params.from_date,
            )
        )
        .offset(params.limit * (params.page))
        .limit(params.limit)
    )
    availability = session.exec(statement).all()
    return availability


@booking_router.post(
    "/teacher-availability", response_model=List[TeacherAvailability]
)
async def create_availability(
    payload: PostAvailabilityPayload,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not current_user.id:
        raise Exception()
    teacher = Teacher.get_teacher_by_user_id(
        session=session, user_id=current_user.id
    )

    await clear_availability(
        session=session,
        teacher_id=teacher.id,
        start=payload.timeframe.start,
        end=payload.timeframe.end,
    )

    availabilities = [
        TeacherAvailability(
            id=event.id,
            start=event.start,
            end=event.end,
            teacher_id=teacher.id,
        )
        for event in payload.events
    ]

    session.add_all(availabilities)
    session.commit()
    return availabilities


@booking_router.delete(
    "/teacher-availability/{availability_id}",
    status_code=status.HTTP_202_ACCEPTED,
)
async def delete_availability(
    availability_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not current_user.id:
        raise Exception()
    teacher = Teacher.get_teacher_by_user_id(
        session=session, user_id=current_user.id
    )
    availability = session.get(TeacherAvailability, availability_id)
    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No availability found by id",
        )
    if not availability.teacher_id == teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this.",
        )
    session.delete(availability)
    session.commit()


@booking_router.put(
    "/teacher-availability/{availability_id}", status_code=status.HTTP_200_OK
)
async def update_availability(
    availability_id: str,
    payload: PostAvailabilityPayloadEvent,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not current_user.id:
        raise Exception()
    teacher = Teacher.get_teacher_by_user_id(
        session=session, user_id=current_user.id
    )
    availability = session.get(TeacherAvailability, availability_id)
    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No availability found by id",
        )
    if not availability.teacher_id == teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this.",
        )
    availability.update(payload)
    await availability.save(session)
    return session.get(TeacherAvailability, availability_id)
