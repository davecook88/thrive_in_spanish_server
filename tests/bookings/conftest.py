from datetime import datetime
import pytest_asyncio
from sqlmodel import Session
from app.db.models.user.user import User, Teacher
from app.db.models.availability.availability_models import TeacherAvailability


@pytest_asyncio.fixture
async def teacher(session: Session, user: User):
    t = Teacher(user_id=user.id)  # type: ignore
    await t.save(session)
    return t


@pytest_asyncio.fixture
async def schedule(session: Session, teacher: User):
    entries = [
        {"start": datetime(2022, 6, 23, 7), "end": datetime(2022, 6, 23, 12)},
        {"start": datetime(2022, 6, 23, 13), "end": datetime(2022, 6, 23, 17)},
        {"start": datetime(2022, 6, 24, 9), "end": datetime(2022, 6, 24, 17)},
    ]
    if not teacher.id:
        raise Exception()
    availabilities = [
        TeacherAvailability(
            id=None, start=e["start"], end=e["end"], teacher_id=teacher.id
        )
        for e in entries
    ]
    session.add_all(availabilities)
    session.commit()
    return availabilities
