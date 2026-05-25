from app.domain.enums.notification_event_type import NotificationEventType
from app.domain.enums.notification_status import NotificationStatus


class TestNotificationServiceCreate:
    def test_create_notification(self, notification_service, notification_repo, event_repo):
        n = notification_service.create_notification("Alerta", "Servidor caiu")

        assert n.title == "Alerta"
        assert n.message == "Servidor caiu"
        assert n.status == NotificationStatus.PENDING

        saved = notification_repo.get_by_id(n.id)
        assert saved is not None
        assert saved.id == n.id

        events = event_repo.get_by_notification_id(n.id)
        assert len(events) == 1
        assert events[0].event_type == NotificationEventType.CREATED

    def test_create_emits_event_with_pending_status(self, notification_service, event_repo):
        n = notification_service.create_notification("T", "M")

        events = event_repo.get_by_notification_id(n.id)
        assert events[0].payload["status"] == "pending"


class TestNotificationServiceGet:
    def test_get_by_id_existing(self, notification_service):
        n = notification_service.create_notification("T", "M")

        result = notification_service.get_notification_by_id(n.id)
        assert result is not None
        assert result.id == n.id

    def test_get_by_id_not_found(self, notification_service):
        result = notification_service.get_notification_by_id("nonexistent")
        assert result is None

    def test_get_all(self, notification_service):
        notification_service.create_notification("A", "1")
        notification_service.create_notification("B", "2")

        result = notification_service.get_all_notifications()
        assert len(result) == 2

    def test_get_all_by_status(self, notification_service):
        n1 = notification_service.create_notification("A", "1")
        notification_service.create_notification("B", "2")
        notification_service.mark_as_sent(n1.id)

        sent = notification_service.get_all_notifications_by_status(NotificationStatus.SENT)
        pending = notification_service.get_all_notifications_by_status(NotificationStatus.PENDING)

        assert len(sent) == 1
        assert sent[0].id == n1.id
        assert len(pending) == 1


class TestNotificationServiceMarkStatus:
    def test_mark_as_sent(self, notification_service, event_repo):
        n = notification_service.create_notification("T", "M")
        notification_service.mark_as_sent(n.id)

        updated = notification_service.get_notification_by_id(n.id)
        assert updated.status == NotificationStatus.SENT

        events = event_repo.get_by_notification_id(n.id)
        event_types = [e.event_type for e in events]
        assert NotificationEventType.SENT in event_types

    def test_mark_as_failed(self, notification_service, event_repo):
        n = notification_service.create_notification("T", "M")
        notification_service.mark_as_failed(n.id, reason="timeout")

        updated = notification_service.get_notification_by_id(n.id)
        assert updated.status == NotificationStatus.FAILED

        events = event_repo.get_by_notification_id(n.id)
        failed_event = [e for e in events if e.event_type == NotificationEventType.FAILED][0]
        assert failed_event.payload["reason"] == "timeout"

    def test_mark_as_processing(self, notification_service, event_repo):
        n = notification_service.create_notification("T", "M")
        notification_service.mark_as_processing(n.id)

        events = event_repo.get_by_notification_id(n.id)
        event_types = [e.event_type for e in events]
        assert NotificationEventType.PROCESSING in event_types

    def test_mark_nonexistent_returns_none(self, notification_service):
        result = notification_service.mark_as_sent("nonexistent")
        assert result is None

    def test_get_events(self, notification_service):
        n = notification_service.create_notification("T", "M")
        notification_service.mark_as_processing(n.id)
        notification_service.mark_as_sent(n.id)

        events = notification_service.get_events(n.id)
        assert len(events) == 3
        assert events[0].event_type == NotificationEventType.CREATED
        assert events[1].event_type == NotificationEventType.PROCESSING
        assert events[2].event_type == NotificationEventType.SENT
