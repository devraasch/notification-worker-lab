from pydantic import BaseModel


class CreateNotificationInput(BaseModel):
    title: str
    message: str
