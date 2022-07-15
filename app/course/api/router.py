from fastapi import Depends, HTTPException, status
from sqlmodel import Session, col
from app.auth.get_current_org import get_current_organization
from app.auth.get_current_user import get_current_user
from app.course.types import CourseBase, CourseFull, CourseUpdatePayload
from app.db.get_session import get_session
from app.db.models.course.course import Course
from app.db.models.user.user import UserFull
from app.organization.model import OrganizationModel

from app.utils.params import ListAPIParams, list_params
from fastapi_utils.inferring_router import InferringRouter


course_router = InferringRouter(
    prefix="/course",
    tags=["course"],
    responses={404: {"description": "Not found"}},
    dependencies=[],
)


@course_router.get("")
def list_courses(
    params: ListAPIParams = Depends(list_params),
    session: Session = Depends(get_session),
    organization: OrganizationModel = Depends(get_current_organization),
    current_user: UserFull = Depends(get_current_user),
):
    offset = params.page * params.limit
    return (
        session.query(Course)
        .filter(col(Course.organization_id) == organization.id)
        .offset(offset)
        .limit(params.limit)
        .all()
    )


@course_router.get("/{course_id}")
def get_course(
    course_id: int,
    session: Session = Depends(get_session),
    organization: OrganizationModel = Depends(get_current_organization),
    current_user: UserFull = Depends(get_current_user),
):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found by ID")
    return course


@course_router.delete("/{course_id}")
def delete_course(
    course_id: int,
    session: Session = Depends(get_session),
    organization: OrganizationModel = Depends(get_current_organization),
    current_user: UserFull = Depends(get_current_user),
):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found by ID")
    session.delete(course)
    session.commit()


@course_router.post("")
def create_course(
    payload: CourseBase,
    session: Session = Depends(get_session),
    organization: OrganizationModel = Depends(get_current_organization),
    current_user: UserFull = Depends(get_current_user),
):
    if not organization.id:
        raise HTTPException(status_code=400)
    course = Course.create_course(
        session=session,
        teacher_ids=payload.teacher_ids,
        organization_id=organization.id,
        difficulty=payload.difficulty,
        description=payload.description,
        name=payload.name,
        price=payload.price,
        max_students=payload.max_students,
        student_ids=payload.student_ids,
    )
    session.add(course)
    session.commit()
    if not course.id:
        raise HTTPException(status_code=400)
    saved_course = session.get(Course, course.id)
    if not saved_course:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Something went wrong saving the course",
        )
    if not saved_course.course_students:
        saved_course.course_students = []
    return CourseFull(
        **saved_course.dict(), course_teachers=saved_course.course_teachers
    )


@course_router.put("/{course_id}")
async def update_course(
    course_id: int,
    payload: CourseUpdatePayload,
    session: Session = Depends(get_session),
    organization: OrganizationModel = Depends(get_current_organization),
    current_user: UserFull = Depends(get_current_user),
):

    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found by ID")
    for key, val in payload.dict().items():
        if key != "teacher_ids":
            course.__setattr__(key, val)

    session.add(course)
    session.commit()
    return course


@course_router.get("/{course_id}/classes")
def get_course_classes(
    course_id: int,
    session: Session = Depends(get_session),
    organization: OrganizationModel = Depends(get_current_organization),
    current_user: UserFull = Depends(get_current_user),
):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found by ID")
    return course.live_classes
