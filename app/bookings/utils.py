from datetime import datetime

from sqlmodel import Session, and_, col, delete

from app.db.models.availability.availability_models import TeacherAvailability


async def clear_availability(
    session: Session, teacher_id: int, start: datetime, end: datetime
):
    statement = delete(TeacherAvailability).where(
        and_(
            col(TeacherAvailability.teacher_id) == teacher_id,
            col(TeacherAvailability.start) > start,
            col(TeacherAvailability.end) < end,
        )
    )
    session.exec(statement)  # type: ignore
