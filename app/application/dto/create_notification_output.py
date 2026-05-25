from datetime import datetime

from pydantic import BaseModel


class CreateNotificationOutput(BaseModel):
    id: str
    title: str
    message: str
    status: str
    created_at: datetime
