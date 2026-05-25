from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.notification_event import NotificationEvent


class NotificationEventRepository(ABC):

    @abstractmethod
    def append(self, event: NotificationEvent) -> None: ...

    @abstractmethod
    def get_by_notification_id(self, notification_id: str) -> List[NotificationEvent]: ...
