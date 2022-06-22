from datetime import datetime
from typing import List, Optional, Union
from pydantic import UUID4, BaseModel, validator


class PostAvailabilityPayloadEvent(BaseModel):
    id: UUID4
    title: Optional[str] = None
    start: datetime
    end: datetime

    @validator("end")
    def end_is_after_start(cls, end: datetime, values: dict):
        start: Union[datetime, None] = values.get("start")
        if not start:
            raise ValueError("No start date")
        if end > start:
            return end
        raise ValueError("end must be after start")


class PostAvailabilityPayloadTimeframe(BaseModel):
    start: datetime
    end: datetime


class PostAvailabilityPayload(BaseModel):
    timeframe: PostAvailabilityPayloadTimeframe
    events: List[PostAvailabilityPayloadEvent]
