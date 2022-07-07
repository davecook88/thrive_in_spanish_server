from typing import Callable, ClassVar, List, Optional, Union, TYPE_CHECKING
from sqlmodel import Field, Relationship, Session
from app.db.base_model import DBModel
from app.db.models.course.exception import CreateCourseException
from app.db.models.user.user import Teacher, Student
from app.organization.model import OrganizationModel

if TYPE_CHECKING:
    from app.db.models.payment.payment import PaymentPackage


class Course(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "course"
    id: Optional[int] = Field(primary_key=True, default=None)
    organization_id: int = Field(foreign_key="organization.id")
    organization: OrganizationModel = Relationship()
    name: str
    description: str
    price: int
    difficulty: int  # Number to help order in terms of difficulty
    course_teachers: List["CourseTeacher"] = Relationship(
        back_populates="course", sa_relationship_kwargs={"cascade": "delete"}
    )
    live_classes: List["LiveClass"] = Relationship(
        back_populates="course", sa_relationship_kwargs={"cascade": "delete"}
    )
    payment_package: "PaymentPackage" = Relationship(
        back_populates="courses", sa_relationship_kwargs={"cascade": "delete"}
    )

    @staticmethod
    def create_course(
        *,
        session: Session,
        teacher_ids: List[int],
        name: str,
        organization_id: int,
        price: int,
        difficulty: int,
        description: str = ""
    ):
        course = Course(
            organization_id=organization_id,
            difficulty=difficulty,
            price=price,
            name=name,
            description=description,
        )
        session.add(course)
        session.commit()
        if not course.id:
            raise CreateCourseException("Error saving course")
        course_teachers = [
            CourseTeacher(teacher_id=teacher_id, course_id=course.id)
            for teacher_id in teacher_ids
        ]
        session.add_all(course_teachers)
        session.commit()
        return course


class LiveClass(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "live_class"
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str
    description: Optional[str] = None
    course: Course = Relationship()
    course_id: int = Field(foreign_key="course.id")
    class_teachers: "ClassTeacher" = Relationship(back_populates="live_class")
    class_students: List["ClassStudent"] = Relationship(
        back_populates="live_class"
    )
    url: str


class CourseTeacher(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "course_teacher"
    id: Optional[int] = Field(primary_key=True, default=None)
    course_id: int = Field(foreign_key=Course.id)
    course: Optional[Course] = Relationship(back_populates="course_teachers")
    teacher_id: int = Field(foreign_key=Teacher.id)
    teacher: Teacher = Relationship(back_populates="course_teacher")
    class_teachers: List["ClassTeacher"] = Relationship(
        back_populates="course_teacher"
    )


class CourseStudent(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "course_student"
    id: Optional[int] = Field(primary_key=True, default=None)
    payment_packages: "PaymentPackage" = Relationship(
        back_populates="course_student"
    )
    payment_package_id: Optional[int] = Field(foreign_key="payment_package.id")
    course: Course = Relationship()
    course_id: int = Field(foreign_key="course.id")
    student_id: int = Field(foreign_key="student.id")
    student: Optional["Student"] = Relationship(back_populates="course_student")
    class_students: List["ClassStudent"] = Relationship(
        back_populates="course_student"
    )


class ClassTeacher(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "class_teacher"
    id: Optional[int] = Field(primary_key=True, default=None)
    class_id: int = Field(foreign_key=LiveClass.id)
    live_class: LiveClass = Relationship(back_populates="class_teachers")
    course_teacher_id: int = Field(foreign_key=CourseTeacher.id)
    course_teacher: Optional[CourseTeacher] = Relationship(
        back_populates="class_teachers",
    )


class ClassStudent(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "class_student"
    id: Optional[int] = Field(primary_key=True, default=None)
    class_id: int = Field(foreign_key=LiveClass.id)
    live_class: LiveClass = Relationship(back_populates="class_students")
    attended: Optional[bool] = False
    course_student_id: int = Field(foreign_key="course_student.id")
    course_student: "CourseStudent" = Relationship(
        back_populates="class_students"
    )
    note: Optional[str]
