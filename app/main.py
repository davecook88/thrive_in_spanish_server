from typing import Dict
from fastapi import FastAPI

from app.bookings.router import booking_router


app = FastAPI()


@app.get("/test")
async def test() -> Dict:
    """
    Test route
    """
    return {"success": True}

app.include_router(booking_router)
