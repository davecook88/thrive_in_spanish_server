from fastapi import Depends, HTTPException
from sqlmodel import Session, col
from app.auth.get_current_org import get_current_organization
from app.auth.get_current_user import get_current_user
from app.course.types import CourseBase, CourseFull, CourseUpdatePayload
from app.db.get_session import get_session
from app.db.models.course.course import Course, CourseTeacher
from app.db.models.user.user import UserFull
from app.organization.model import OrganizationModel

from app.utils.params import ListAPIParams, list_params
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter


course_router = InferringRouter(
    prefix="/courses",
    tags=["courses"],
    responses={404: {"description": "Not found"}},
    dependencies=[],
)


@cbv(course_router)
class CourseRoutes:
    session: Session = Depends(get_session)
    organization: OrganizationModel = Depends(get_current_organization)
    current_user: UserFull = Depends(get_current_user)

    @course_router.get("")
    def list_courses(self, params: ListAPIParams = Depends(list_params)):
        offset = params.page * params.limit
        return (
            self.session.query(Course)
            .filter(col(Course.organization_id == self.organization.id))
            .offset(offset)
            .limit(params.limit)
            .all()
        )

    @course_router.get("/{course_id}")
    def get_course(self, course_id: int):
        course = self.session.get(Course, course_id)
        if not course:
            raise HTTPException(
                status_code=404, detail="Course not found by ID"
            )
        return course

    @course_router.delete("/{course_id}")
    def delete_course(self, course_id: int):
        course = self.session.get(Course, course_id)
        if not course:
            raise HTTPException(
                status_code=404, detail="Course not found by ID"
            )
        self.session.delete(course)
        self.session.commit()

    @course_router.post("")
    def create_course(self, payload: CourseBase):
        if not self.organization.id:
            raise HTTPException(status_code=400)
        course = Course(
            organization_id=self.organization.id,
            difficulty=payload.difficulty,
            description=payload.description,
            name=payload.name,
            price=payload.price,
        )
        self.session.add(course)
        self.session.commit()
        if not course.id:
            raise HTTPException(status_code=400)
        course_teacher = CourseTeacher(
            course_id=course.id, teacher_id=payload.teacher_id
        )
        self.session.add(course_teacher)
        self.session.commit()
        return CourseFull(**course.dict(), course_teachers=[course_teacher])

    @course_router.put("/{course_id}")
    async def update_course(self, course_id: int, payload: CourseUpdatePayload):
        course = self.session.get(Course, course_id)
        if not course:
            raise HTTPException(
                status_code=404, detail="Course not found by ID"
            )
        for key, val in payload.dict():
            course.__setattr__(key, val)
        self.session.add(course)
        self.session.commit()
        return course

    @course_router.get("/{course_id}/classes")
    def get_course_classes(self, course_id: int):
        course = self.session.get(Course, course_id)
        if not course:
            raise HTTPException(
                status_code=404, detail="Course not found by ID"
            )
        return course.live_classes
