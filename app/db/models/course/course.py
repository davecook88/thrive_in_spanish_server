from typing import Callable, ClassVar, List, Optional, Union, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.db.base_model import DBModel
from app.db.models.user.user import Teacher, Student
from app.organization.model import OrganizationModel

if TYPE_CHECKING:
    from app.db.models.payment.payment import PaymentPackage


class Course(DBModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    organization_id: int = Field(foreign_key="organization.id")
    organization: OrganizationModel = Relationship()
    name: str
    description: str
    price: int
    difficulty: int  # Number to help order in terms of difficulty
    course_teachers: List["CourseTeacher"] = Relationship(
        back_populates="course"
    )
    live_classes: List["LiveClass"] = Relationship(back_populates="course")


class LiveClass(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "live_class"
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str
    description: Optional[str] = None
    course: Course = Relationship()
    course_id: int = Field(foreign_key="course.id")
    class_teacher: "ClassTeacher" = Relationship(back_populates="live_class")
    url: str


class CourseTeacher(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "course_teacher"
    id: Optional[int] = Field(primary_key=True, default=None)
    course_id: int = Field(foreign_key=Course.id)
    course: Course = Relationship(back_populates="course.course_teachers")
    teacher_id: int = Field(foreign_key=Teacher.id)
    teacher: Teacher = Relationship(back_populates="course_teacher")


class CourseStudent(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "course_student"
    payment_package: "PaymentPackage" = Relationship(
        back_populates="course_student"
    )
    payment_package_id: Optional[int] = Field(foreign_key="payment_package.id")
    course: Course = Relationship()
    course_id: int = Field(foreign_key="course.id")
    student_id: int = Field(foreign_key="student.id")
    student: "Student"


class ClassTeacher(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "class_teacher"
    id: Optional[int] = Field(primary_key=True, default=None)
    class_id: int = Field(foreign_key=LiveClass.id)
    live_class: LiveClass = Relationship(back_populates="class_teacher")
    teacher_id: int = Field(foreign_key=Teacher.id)
    teacher: Teacher = Relationship(back_populates="course_teacher")


class ClassStudent(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "class_student"
    id: Optional[int] = Field(primary_key=True, default=None)
    class_id: int = Field(foreign_key=LiveClass.id)
    live_class: LiveClass = Relationship(back_populates="class_teacher")
    attended: Optional[bool] = False
    student_id: int = Field(foreign_key="student.id")
    student: "Student"
    note: Optional[str]
