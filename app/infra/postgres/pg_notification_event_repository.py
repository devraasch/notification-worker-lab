import logging
from typing import List

from app.domain.entities.notification_event import NotificationEvent
from app.domain.enums.notification_event_type import NotificationEventType
from app.domain.repositories.notification_event_repository import NotificationEventRepository
from app.infra.postgres.database import SessionLocal
from app.infra.postgres.models import NotificationEventModel

logger = logging.getLogger(__name__)


class PgNotificationEventRepository(NotificationEventRepository):

    def append(self, event: NotificationEvent) -> None:
        session = SessionLocal()
        try:
            model = NotificationEventModel(
                id=event.id,
                notification_id=event.notification_id,
                event_type=event.event_type.value,
                event_version=event.event_version,
                payload=event.payload,
                created_at=event.created_at,
            )
            session.add(model)
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Erro ao inserir evento %s", event.id)
            raise
        finally:
            session.close()

    def get_by_notification_id(self, notification_id: str) -> List[NotificationEvent]:
        session = SessionLocal()
        try:
            rows = (
                session.query(NotificationEventModel)
                .filter(NotificationEventModel.notification_id == notification_id)
                .order_by(NotificationEventModel.created_at.asc())
                .all()
            )
            return [
                NotificationEvent(
                    id=str(row.id),
                    notification_id=str(row.notification_id),
                    event_type=NotificationEventType(row.event_type),
                    event_version=row.event_version,
                    payload=row.payload,
                    created_at=row.created_at,
                )
                for row in rows
            ]
        finally:
            session.close()
