from enum import Enum


class NotificationEventType(Enum):
    CREATED = "notification.created"
    PROCESSING = "notification.processing"
    SENT = "notification.sent"
    FAILED = "notification.failed"