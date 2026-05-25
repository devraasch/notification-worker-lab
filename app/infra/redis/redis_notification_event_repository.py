from typing import List

from redis import Redis

from app.domain.entities.notification_event import NotificationEvent
from app.domain.repositories.notification_event_repository import NotificationEventRepository

EVENT_PREFIX = "notification_events:"


class RedisNotificationEventRepository(NotificationEventRepository):

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    def _key(self, notification_id: str) -> str:
        return f"{EVENT_PREFIX}{notification_id}"

    def append(self, event: NotificationEvent) -> None:
        self.redis_client.rpush(self._key(event.notification_id), event.to_json())

    def get_by_notification_id(self, notification_id: str) -> List[NotificationEvent]:
        raw_list = self.redis_client.lrange(self._key(notification_id), 0, -1)
        return [NotificationEvent.from_json(raw) for raw in raw_list]
