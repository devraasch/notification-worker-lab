from typing import List

from fastapi import APIRouter, HTTPException

from app.application.dto.create_notification_input import CreateNotificationInput
from app.application.use_cases.create_notification import CreateNotificationUseCase
from app.application.use_cases.get_notification import (
    GetAllNotificationsByStatusUseCase,
    GetAllNotificationsUseCase,
    GetNotificationUseCase,
)
from app.domain.enums.notification_status import NotificationStatus
from app.presentation.api.dependencies import notification_service, publisher
from app.presentation.api.schemas.notification_schema import (
    NotificationRequest,
    NotificationResponse,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/", response_model=NotificationResponse, status_code=201)
def create_notification(body: NotificationRequest):
    use_case = CreateNotificationUseCase(notification_service, publisher)
    result = use_case.execute(
        CreateNotificationInput(title=body.title, message=body.message)
    )
    return result


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: str):
    use_case = GetNotificationUseCase(notification_service)
    result = use_case.execute(notification_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    return result


@router.get("/", response_model=List[NotificationResponse])
def get_all_notifications():
    use_case = GetAllNotificationsUseCase(notification_service)
    return use_case.execute()


@router.get("/status/{status}", response_model=List[NotificationResponse])
def get_all_notifications_by_status(status: NotificationStatus):
    use_case = GetAllNotificationsByStatusUseCase(notification_service)
    return use_case.execute(status)
