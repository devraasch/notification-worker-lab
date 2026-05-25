import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from app.domain.enums.notification_event_type import NotificationEventType


@dataclass
class NotificationEvent:
    notification_id: str
    event_type: NotificationEventType
    payload: dict
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        notification_id: str,
        event_type: NotificationEventType,
        payload: dict | None = None,
    ) -> "NotificationEvent":
        return cls(
            notification_id=notification_id,
            event_type=event_type,
            payload=payload or {},
        )

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "notification_id": self.notification_id,
            "event_type": self.event_type.value,
            "payload": self.payload,
            "created_at": self.created_at.isoformat(),
        })

    @classmethod
    def from_json(cls, data: str | bytes) -> "NotificationEvent":
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        raw = json.loads(data)
        return cls(
            id=raw["id"],
            notification_id=raw["notification_id"],
            event_type=NotificationEventType(raw["event_type"]),
            payload=raw["payload"],
            created_at=datetime.fromisoformat(raw["created_at"]),
        )
