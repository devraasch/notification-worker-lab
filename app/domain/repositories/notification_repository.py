from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from app.domain.entities.notification import Notification
from app.domain.enums.notification_status import NotificationStatus


class NotificationRepository(ABC):

    @abstractmethod
    def save(self, notification: Notification) -> None: ...

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Notification]: ...

    @abstractmethod
    def get_all(self) -> List[Notification]: ...

    @abstractmethod
    def get_all_by_status(self, status: NotificationStatus) -> List[Notification]: ...
