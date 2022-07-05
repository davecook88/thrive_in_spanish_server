from app.core.config import settings


async def get_stripe_api_key() -> str:
    return settings.STRIPE_API_KEY
