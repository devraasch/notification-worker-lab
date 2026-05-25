from unittest.mock import MagicMock, patch

from app.domain.enums.notification_event_type import NotificationEventType
from app.domain.enums.notification_status import NotificationStatus
from app.infra.workers.notification_worker import NotificationWorker


class TestNotificationWorker:
    @patch("app.infra.workers.notification_worker.RabbitMQConsumer")
    def test_processes_valid_message(self, mock_consumer_cls, notification_service, event_repo):
        n = notification_service.create_notification("Alerta", "Disco cheio")

        worker = NotificationWorker(notification_service)
        worker._handle_message({"notification_id": n.id})

        updated = notification_service.get_notification_by_id(n.id)
        assert updated.status == NotificationStatus.SENT

        events = event_repo.get_by_notification_id(n.id)
        event_types = [e.event_type for e in events]
        assert NotificationEventType.CREATED in event_types
        assert NotificationEventType.PROCESSING in event_types
        assert NotificationEventType.SENT in event_types

    @patch("app.infra.workers.notification_worker.RabbitMQConsumer")
    def test_ignores_message_without_notification_id(self, mock_consumer_cls, notification_service):
        worker = NotificationWorker(notification_service)
        worker._handle_message({})

    @patch("app.infra.workers.notification_worker.RabbitMQConsumer")
    def test_ignores_nonexistent_notification(self, mock_consumer_cls, notification_service):
        worker = NotificationWorker(notification_service)
        worker._handle_message({"notification_id": "nonexistent"})

    @patch("app.infra.workers.notification_worker.RabbitMQConsumer")
    def test_ignores_already_sent(self, mock_consumer_cls, notification_service, event_repo):
        n = notification_service.create_notification("T", "M")
        notification_service.mark_as_sent(n.id)
        events_before = len(event_repo.get_by_notification_id(n.id))

        worker = NotificationWorker(notification_service)
        worker._handle_message({"notification_id": n.id})

        events_after = len(event_repo.get_by_notification_id(n.id))
        assert events_after == events_before

    @patch("app.infra.workers.notification_worker.RabbitMQConsumer")
    def test_ignores_already_failed(self, mock_consumer_cls, notification_service, event_repo):
        n = notification_service.create_notification("T", "M")
        notification_service.mark_as_failed(n.id, reason="erro")
        events_before = len(event_repo.get_by_notification_id(n.id))

        worker = NotificationWorker(notification_service)
        worker._handle_message({"notification_id": n.id})

        events_after = len(event_repo.get_by_notification_id(n.id))
        assert events_after == events_before

    @patch("app.infra.workers.notification_worker.RabbitMQConsumer")
    def test_marks_as_failed_on_exception(self, mock_consumer_cls, notification_service):
        n = notification_service.create_notification("T", "M")

        worker = NotificationWorker(notification_service)
        notification_service.mark_as_processing = MagicMock(side_effect=RuntimeError("boom"))

        worker._handle_message({"notification_id": n.id})

        updated = notification_service.get_notification_by_id(n.id)
        assert updated.status == NotificationStatus.FAILED
