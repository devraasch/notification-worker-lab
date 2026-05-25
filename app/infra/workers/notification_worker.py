import logging

from app.domain.enums.notification_status import NotificationStatus
from app.domain.services.notification_service import NotificationService
from app.infra.rabbitmq.consumer import RabbitMQConsumer

logger = logging.getLogger(__name__)


class NotificationWorker:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service
        self.consumer = RabbitMQConsumer(on_message=self._handle_message)

    def _handle_message(self, message: dict) -> None:
        notification_id = message.get("notification_id")

        if not notification_id:
            logger.warning("Mensagem sem notification_id: %s", message)
            return

        notification = self.notification_service.get_notification_by_id(notification_id)

        if not notification:
            logger.warning("Notificação não encontrada: %s", notification_id)
            return

        if notification.status == NotificationStatus.SENT:
            logger.info(
                "Notificação %s já foi enviada. Ignorando mensagem duplicada.",
                notification.id,
            )
            return

        if notification.status == NotificationStatus.FAILED:
            logger.info(
                "Notificação %s já está marcada como failed. Ignorando.",
                notification.id,
            )
            return

        try:
            logger.info(
                "Processando notificação %s: %s",
                notification.id,
                notification.title,
            )

            self.notification_service.mark_as_sent(notification.id)

            logger.info("Notificação %s marcada como enviada", notification.id)

        except Exception:
            logger.exception("Falha ao processar notificação %s", notification.id)
            self.notification_service.mark_as_failed(notification.id)

    def run(self) -> None:
        logger.info("Iniciando notification worker...")
        self.consumer.start()