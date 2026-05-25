from typing import List, Optional

from app.domain.entities.notification import Notification
from app.domain.entities.notification_event import NotificationEvent
from app.domain.enums.notification_event_type import NotificationEventType
from app.domain.enums.notification_status import NotificationStatus
from app.domain.repositories.notification_event_repository import NotificationEventRepository
from app.domain.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(
        self,
        notification_repository: NotificationRepository,
        event_repository: NotificationEventRepository,
    ):
        self.notification_repository = notification_repository
        self.event_repository = event_repository

    def _emit(
        self,
        notification: Notification,
        event_type: NotificationEventType,
        extra: dict | None = None,
    ) -> None:
        event = NotificationEvent.create(
            notification_id=notification.id,
            event_type=event_type,
            payload={"status": notification.status.value, **(extra or {})},
        )
        self.event_repository.append(event)

    def create_notification(self, title: str, message: str) -> Notification:
        notification = Notification(title=title, message=message)
        self.notification_repository.save(notification)
        self._emit(notification, NotificationEventType.CREATED)
        return notification

    def get_notification_by_id(self, id: str) -> Optional[Notification]:
        return self.notification_repository.get_by_id(id)

    def get_all_notifications(self) -> List[Notification]:
        return self.notification_repository.get_all()

    def get_all_notifications_by_status(self, status: NotificationStatus) -> List[Notification]:
        return self.notification_repository.get_all_by_status(status)

    def mark_as_processing(self, id: str) -> Optional[Notification]:
        notification = self.notification_repository.get_by_id(id)
        if notification:
            notification.status = NotificationStatus.PENDING
            self.notification_repository.save(notification)
            self._emit(notification, NotificationEventType.PROCESSING)
        return notification

    def mark_as_sent(self, id: str) -> Optional[Notification]:
        notification = self.notification_repository.get_by_id(id)
        if notification:
            notification.status = NotificationStatus.SENT
            self.notification_repository.save(notification)
            self._emit(notification, NotificationEventType.SENT)
        return notification

    def mark_as_failed(self, id: str, reason: str = "") -> Optional[Notification]:
        notification = self.notification_repository.get_by_id(id)
        if notification:
            notification.status = NotificationStatus.FAILED
            self.notification_repository.save(notification)
            self._emit(
                notification,
                NotificationEventType.FAILED,
                extra={"reason": reason},
            )
        return notification

    def get_events(self, notification_id: str) -> List[NotificationEvent]:
        return self.event_repository.get_by_notification_id(notification_id)
