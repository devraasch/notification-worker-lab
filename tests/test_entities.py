import json

from app.domain.entities.notification import Notification
from app.domain.entities.notification_event import NotificationEvent
from app.domain.enums.notification_event_type import NotificationEventType
from app.domain.enums.notification_status import NotificationStatus


class TestNotification:
    def test_create_with_defaults(self):
        n = Notification(title="Alerta", message="Servidor caiu")

        assert n.title == "Alerta"
        assert n.message == "Servidor caiu"
        assert n.status == NotificationStatus.PENDING
        assert n.id is not None
        assert n.created_at is not None

    def test_to_json_and_from_json_roundtrip(self):
        n = Notification(title="Teste", message="Mensagem")
        data = n.to_json()
        restored = Notification.from_json(data)

        assert restored.id == n.id
        assert restored.title == n.title
        assert restored.message == n.message
        assert restored.status == n.status
        assert restored.created_at == n.created_at

    def test_from_json_accepts_bytes(self):
        n = Notification(title="Bytes", message="Test")
        data = n.to_json().encode("utf-8")
        restored = Notification.from_json(data)

        assert restored.id == n.id

    def test_to_json_contains_all_fields(self):
        n = Notification(title="T", message="M")
        payload = json.loads(n.to_json())

        assert set(payload.keys()) == {"id", "title", "message", "status", "created_at"}

    def test_status_values(self):
        assert NotificationStatus.PENDING.value == "pending"
        assert NotificationStatus.SENT.value == "sent"
        assert NotificationStatus.FAILED.value == "failed"


class TestNotificationEvent:
    def test_create_factory(self):
        event = NotificationEvent.create(
            notification_id="abc-123",
            event_type=NotificationEventType.CREATED,
            payload={"status": "pending"},
        )

        assert event.notification_id == "abc-123"
        assert event.event_type == NotificationEventType.CREATED
        assert event.payload == {"status": "pending"}
        assert event.event_version == 1
        assert event.id is not None

    def test_create_with_custom_version(self):
        event = NotificationEvent.create(
            notification_id="abc",
            event_type=NotificationEventType.SENT,
            event_version=2,
        )

        assert event.event_version == 2

    def test_create_with_none_payload_defaults_to_empty_dict(self):
        event = NotificationEvent.create(
            notification_id="abc",
            event_type=NotificationEventType.PROCESSING,
            payload=None,
        )

        assert event.payload == {}

    def test_to_json_and_from_json_roundtrip(self):
        event = NotificationEvent.create(
            notification_id="xyz",
            event_type=NotificationEventType.FAILED,
            payload={"reason": "timeout"},
            event_version=3,
        )
        data = event.to_json()
        restored = NotificationEvent.from_json(data)

        assert restored.id == event.id
        assert restored.notification_id == event.notification_id
        assert restored.event_type == event.event_type
        assert restored.event_version == event.event_version
        assert restored.payload == event.payload
        assert restored.created_at == event.created_at

    def test_from_json_accepts_bytes(self):
        event = NotificationEvent.create(
            notification_id="x", event_type=NotificationEventType.CREATED
        )
        data = event.to_json().encode("utf-8")
        restored = NotificationEvent.from_json(data)

        assert restored.id == event.id

    def test_from_json_missing_version_defaults_to_1(self):
        raw = json.dumps({
            "id": "aaa",
            "notification_id": "bbb",
            "event_type": "notification.created",
            "payload": {},
            "created_at": "2026-01-01T00:00:00+00:00",
        })
        restored = NotificationEvent.from_json(raw)

        assert restored.event_version == 1

    def test_event_type_values(self):
        assert NotificationEventType.CREATED.value == "notification.created"
        assert NotificationEventType.PROCESSING.value == "notification.processing"
        assert NotificationEventType.SENT.value == "notification.sent"
        assert NotificationEventType.FAILED.value == "notification.failed"
