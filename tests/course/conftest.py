import pytest
from sqlmodel import Session

from app.db.models.course.course import Course
from app.db.models.user.user import TeacherFull


@pytest.fixture
def course(session: Session, teacher: TeacherFull):
    c = Course(
        name="test course",
        description="description",
        difficulty=1,
        organization_id=teacher.user.organization_id,
        price=1000,
    )
    session.add(c)
    session.commit()
