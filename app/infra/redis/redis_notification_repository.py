from typing import List, Optional

from redis import Redis

from app.domain.entities.notification import Notification
from app.domain.enums.notification_status import NotificationStatus
from app.domain.repositories.notification_repository import NotificationRepository

NOTIFICATION_PREFIX = "notification:"


class RedisNotificationRepository(NotificationRepository):

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    def _key(self, id: str) -> str:
        return f"{NOTIFICATION_PREFIX}{id}"

    def save(self, notification: Notification) -> None:
        self.redis_client.set(self._key(notification.id), notification.to_json())

    def get_by_id(self, id: str) -> Optional[Notification]:
        data = self.redis_client.get(self._key(id))
        if data is None:
            return None
        return Notification.from_json(data)

    def get_all(self) -> List[Notification]:
        notifications: list[Notification] = []
        for key in self.redis_client.scan_iter(f"{NOTIFICATION_PREFIX}*"):
            data = self.redis_client.get(key)
            if data:
                notifications.append(Notification.from_json(data))
        return notifications

    def get_all_by_status(self, status: NotificationStatus) -> List[Notification]:
        return [n for n in self.get_all() if n.status == status]
