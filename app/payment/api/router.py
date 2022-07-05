from typing import Dict, Literal
from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel
from sqlmodel import Session
from stripe import PaymentIntent
from app.core.config import settings


from app.db.get_session import get_session

import stripe
from app.payment.api.dependencies import get_stripe_api_key


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
):
    stripe.api_key = stripe_api_key
    intent = stripe.PaymentIntent.create(
        amount=payload.amount,
        currency=payload.currency,
        metadata={"course_package": payload.course_package},
    )
    return {"secret": intent["client_secret"]}


@payment_router.post("/stripe-webhook")
async def receive_stripe_webhook(
    request: Request,
    stripe_signature: str = Header(str),
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
        print(payment_intent)
    # ... handle other event types
    else:
        print("Unhandled event type {}".format(event["type"]))
