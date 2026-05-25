from typing import List, Optional

from app.application.dto.create_notification_output import CreateNotificationOutput
from app.domain.enums.notification_status import NotificationStatus
from app.domain.services.notification_service import NotificationService


def _to_output(notification) -> CreateNotificationOutput:
    return CreateNotificationOutput(
        id=notification.id,
        title=notification.title,
        message=notification.message,
        status=notification.status.value,
        created_at=notification.created_at,
    )


class GetNotificationUseCase:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def execute(self, id: str) -> Optional[CreateNotificationOutput]:
        notification = self.notification_service.get_notification_by_id(id)
        if notification is None:
            return None
        return _to_output(notification)


class GetAllNotificationsUseCase:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def execute(self) -> List[CreateNotificationOutput]:
        return [_to_output(n) for n in self.notification_service.get_all_notifications()]


class GetAllNotificationsByStatusUseCase:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def execute(self, status: NotificationStatus) -> List[CreateNotificationOutput]:
        return [
            _to_output(n)
            for n in self.notification_service.get_all_notifications_by_status(status)
        ]
