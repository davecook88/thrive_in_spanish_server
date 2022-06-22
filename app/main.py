from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.bookings.router import booking_router
from app.auth.router import auth_router


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/test")
async def test() -> Dict:
    """
    Test route
    """
    return {"success": True}


app.include_router(booking_router)
app.include_router(auth_router)
