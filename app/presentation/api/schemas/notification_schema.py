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


class NotificationEventResponse(BaseModel):
    id: str
    notification_id: str
    event_type: str
    event_version: int
    payload: dict
    created_at: datetime
