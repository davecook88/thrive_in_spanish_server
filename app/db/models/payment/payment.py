from datetime import datetime
from typing import ClassVar, List, Optional, Union, Callable

from sqlmodel import Relationship, Session, Field
from stripe import PaymentIntent
from app.db.base_model import DBModel
from app.db.models.course.course import Course, CourseStudent
from app.db.models.user.user import Student, User, UserFull
from app.payment.api.types import StripePaymentIntentMetadata


class PaymentModelException(Exception):
    pass


class Payment(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "payment"
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship()
    amount: int  # Number to help order in terms of difficulty
    payment_date: datetime = datetime.utcnow()
    payment_package: "PaymentPackage" = Relationship(back_populates="payment")

    @staticmethod
    def register_stripe_payment_intent(
        session: Session, payment_intent: PaymentIntent
    ) -> "Payment":
        metadata = StripePaymentIntentMetadata(**payment_intent["metadata"])
        user: Optional[UserFull] = (
            session.query(User)
            .filter(User.google_id == metadata.user_google_id)
            .first()
        )
        if not user:
            raise PaymentModelException(
                f"User not found for google id {metadata.user_google_id}"
            )
        payment = Payment(user_id=user.id, amount=payment_intent["amount"])
        session.add(payment)
        session.commit()
        return payment


class PaymentPackage(DBModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "payment_package"
    id: Optional[int] = Field(primary_key=True, default=None)
    payment_id: Optional[int] = Field(foreign_key=Payment.id)
    payment: "Payment" = Relationship(
        back_populates="payment_package",
        sa_relationship_kwargs={"cascade": "delete"},
    )
    course_id: Optional[int] = Field(foreign_key=Course.id)
    courses: List[Course] = Relationship(back_populates="payment_package")
    package_limitations: List["PaymentPackageLimitations"] = Relationship(
        back_populates="payment_package",
        sa_relationship_kwargs={"cascade": "delete"},
    )
    student_id: int = Field(foreign_key="student.id")
    student: Student = Relationship(back_populates="payment_packages")
    courses_booked: int
    courses_bought: int
    course_student: CourseStudent = Relationship(
        back_populates="payment_packages"
    )

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
