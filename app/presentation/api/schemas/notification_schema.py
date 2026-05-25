from datetime import datetime

from pydantic import BaseModel


class NotificationRequest(BaseModel):
    title: str
    message: str


class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    status: str
    created_at: datetime
