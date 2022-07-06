from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from pydantic import BaseModel
from sqlmodel import Session
from stripe import PaymentIntent
from app.auth.get_current_user import get_current_user
from app.core.config import settings
from app.db.models.payment.payment import Payment


from app.db.get_session import get_session

import stripe
from app.db.models.user.user import UserFull
from app.payment.api.dependencies import get_stripe_api_key
from app.payment.api.types import StripePaymentIntentMetadata


payment_router = APIRouter(
    prefix="/payment",
    tags=["payment"],
    responses={404: {"description": "Not found"}},
    dependencies=[],
)


class CreatePaymentIntentPayload(BaseModel):
    amount: int
    currency: Literal["usd"]
    course_package: str


@payment_router.post("/create-payment-intent")
async def create_payment_intent(
    payload: CreatePaymentIntentPayload,
    stripe_api_key: str = Depends(get_stripe_api_key),
    session: Session = Depends(get_session),
    current_user: UserFull = Depends(get_current_user),
):
    stripe.api_key = stripe_api_key
    if not current_user.google_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Couldn't get a Google ID for current user",
        )
    metadata = StripePaymentIntentMetadata(
        course_package=payload.course_package,
        user_google_id=current_user.google_id,
    )
    intent = stripe.PaymentIntent.create(
        amount=payload.amount,
        currency=payload.currency,
        metadata=metadata.__dict__,
    )
    return {"secret": intent["client_secret"]}


@payment_router.post("/stripe-webhook")
async def receive_stripe_webhook(
    request: Request,
    stripe_signature: str = Header(str),
    session: Session = Depends(get_session),
):
    event = None
    data = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload=data,
            sig_header=stripe_signature,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:  # type: ignore
        # Invalid signature
        raise e
    if event["type"] == "payment_intent.succeeded":
        payment_intent: PaymentIntent = event["data"]["object"]

        Payment.register_stripe_payment_intent(
            session=session, payment_intent=payment_intent
        )

    # ... handle other event types
    else:
        print("Unhandled event type {}".format(event["type"]))
