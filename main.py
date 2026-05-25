"""Entrypoint para o worker de notificações."""
import logging
import sys

from redis import Redis

from app.config.settings import settings
from app.domain.services.notification_service import NotificationService
from app.infra.redis.redis_notification_event_repository import RedisNotificationEventRepository
from app.infra.redis.redis_notification_repository import RedisNotificationRepository
from app.infra.workers.notification_worker import NotificationWorker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Iniciando Notification Worker...")

    redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    repository = RedisNotificationRepository(redis_client)
    event_repository = RedisNotificationEventRepository(redis_client)
    service = NotificationService(repository, event_repository)
    worker = NotificationWorker(service)

    try:
        worker.run()
    except KeyboardInterrupt:
        logger.info("Worker encerrado pelo usuário")
        sys.exit(0)


if __name__ == "__main__":
    main()
