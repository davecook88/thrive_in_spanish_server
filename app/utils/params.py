from pydantic import BaseModel

from app.core.config import settings


class ListAPIParams(BaseModel):
    """
    Base model for list API routes
    specifies query params relating to
    pagination
    """

    limit: int = 100
    page: int = 0


async def list_params(limit: int = settings.DEFAULT_PAGE_SIZE, page: int = 0):
    try:
        params = ListAPIParams(limit=limit, page=page)
        return params
    except Exception as e:
        print(e)
