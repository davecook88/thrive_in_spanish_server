from dataclasses import dataclass


@dataclass
class StripePaymentIntentMetadata:
    course_package: str
    user_google_id: str
