from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class ProcessRequest(BaseModel):
    data: str = Field(..., min_length=1, description="Data to process")
    priority: int = Field(default=1, ge=1, le=5, description="Priority 1-5")


class ProcessResponse(BaseModel):
    request_id: str
    status: str
    result: str
    data_length: int


class MessageOut(BaseModel):
    id: int
    text: str
    author: str
    created_at: datetime

    model_config = {"from_attributes": True}
