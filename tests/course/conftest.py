import pytest
from sqlmodel import Session

from app.db.models.course.course import Course
from app.db.models.user.user import Teacher


@pytest.fixture
def course(session: Session, teacher: Teacher):
    if not teacher.id:
        raise Exception()
    c = Course.create_course(
        session=session,
        teacher_ids=[teacher.id],
        name="test course",
        description="description",
        difficulty=1,
        organization_id=teacher.user.organization_id,
        price=1000,
    )
    return session.get(Course, c.id)
