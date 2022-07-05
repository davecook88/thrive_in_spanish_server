from datetime import datetime
from typing import ClassVar, List, Optional, Union, Callable

from pydantic import Field
from sqlmodel import Relationship
from app.db.base_model import DBModel
from app.db.models.course.course import Course
from app.db.models.user.user import Student, UserFull


class Payment(DBModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    user: UserFull = Relationship()
    amount: int  # Number to help order in terms of difficulty
    payment_date: datetime = datetime.utcnow()
    package_id: int = Field(foreign_key="payment_package.id")
    package: "PaymentPackage" = Relationship()


class PaymentPackage(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "payment_package"
    id: Optional[int] = Field(primary_key=True, default=None)
    payment_id: int = Field(foreign_key="payment.id")
    payment: Payment = Relationship()
    courses: List[Course] = Relationship(back_populates="payment_package")
    package_limitations: List["PaymentPackageLimitations"] = Relationship(
        back_populates="payment_package"
    )
    student_id: int = Field(foreign_key="student.id")
    student: Student = Relationship(back_populates="payment_packages")
    courses_booked: int
    courses_bought: int

    @property
    def courses_remaining(self):
        return self.courses_bought - self.courses_booked


class PaymentPackageLimitations(DBModel, table=True):
    """
    If a payment may only be used to book a specific kind of class, this
    table specifies which can be bought.

    Each row can be seen as an "allowance" and when it is used,
    it will be marked "used"
    """

    __tablename__: ClassVar[
        Union[str, Callable[..., str]]
    ] = "payment_package_limitations"
    id: Optional[int] = Field(primary_key=True, default=None)
    used: bool = False
    course_permitted: str
    payment_package_id: int = Field(foreign_key="payment_package.id")
    payment_package: PaymentPackage = Relationship(
        back_populates="package_limitations"
    )
