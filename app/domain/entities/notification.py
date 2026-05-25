import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.enums.notification_status import NotificationStatus


@dataclass
class Notification:
    title: str
    message: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
        })

    @classmethod
    def from_json(cls, data: str | bytes) -> "Notification":
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        payload = json.loads(data)
        return cls(
            id=payload["id"],
            title=payload["title"],
            message=payload["message"],
            status=NotificationStatus(payload["status"]),
            created_at=datetime.fromisoformat(payload["created_at"]),
        )
