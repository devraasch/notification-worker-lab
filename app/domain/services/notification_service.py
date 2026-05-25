from typing import List, Optional

from app.domain.entities.notification import Notification
from app.domain.enums.notification_status import NotificationStatus
from app.domain.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository

    def create_notification(self, title: str, message: str) -> Notification:
        notification = Notification(title=title, message=message)
        self.notification_repository.save(notification)
        return notification

    def get_notification_by_id(self, id: str) -> Optional[Notification]:
        return self.notification_repository.get_by_id(id)

    def get_all_notifications(self) -> List[Notification]:
        return self.notification_repository.get_all()

    def get_all_notifications_by_status(self, status: NotificationStatus) -> List[Notification]:
        return self.notification_repository.get_all_by_status(status)

    def mark_as_sent(self, id: str) -> Optional[Notification]:
        notification = self.notification_repository.get_by_id(id)
        if notification:
            notification.status = NotificationStatus.SENT
            self.notification_repository.save(notification)
        return notification

    def mark_as_failed(self, id: str) -> Optional[Notification]:
        notification = self.notification_repository.get_by_id(id)
        if notification:
            notification.status = NotificationStatus.FAILED
            self.notification_repository.save(notification)
        return notification
