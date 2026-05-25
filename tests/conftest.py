from typing import List, Optional
from unittest.mock import MagicMock

import pytest

from app.domain.entities.notification import Notification
from app.domain.entities.notification_event import NotificationEvent
from app.domain.enums.notification_status import NotificationStatus
from app.domain.repositories.notification_event_repository import NotificationEventRepository
from app.domain.repositories.notification_repository import NotificationRepository
from app.domain.services.notification_service import NotificationService


class InMemoryNotificationRepository(NotificationRepository):
    def __init__(self):
        self._store: dict[str, Notification] = {}

    def save(self, notification: Notification) -> None:
        self._store[notification.id] = notification

    def get_by_id(self, id: str) -> Optional[Notification]:
        return self._store.get(id)

    def get_all(self) -> List[Notification]:
        return list(self._store.values())

    def get_all_by_status(self, status: NotificationStatus) -> List[Notification]:
        return [n for n in self._store.values() if n.status == status]


class InMemoryNotificationEventRepository(NotificationEventRepository):
    def __init__(self):
        self._store: list[NotificationEvent] = []

    def append(self, event: NotificationEvent) -> None:
        self._store.append(event)

    def get_by_notification_id(self, notification_id: str) -> List[NotificationEvent]:
        return [e for e in self._store if e.notification_id == notification_id]


@pytest.fixture
def notification_repo():
    return InMemoryNotificationRepository()


@pytest.fixture
def event_repo():
    return InMemoryNotificationEventRepository()


@pytest.fixture
def notification_service(notification_repo, event_repo):
    return NotificationService(notification_repo, event_repo)


@pytest.fixture
def mock_publisher():
    return MagicMock()
