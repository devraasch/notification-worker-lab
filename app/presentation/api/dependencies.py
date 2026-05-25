from redis import Redis

from app.config.settings import settings
from app.domain.services.notification_service import NotificationService
from app.infra.rabbitmq.publisher import RabbitMQPublisher
from app.infra.redis.redis_notification_event_repository import RedisNotificationEventRepository
from app.infra.redis.redis_notification_repository import RedisNotificationRepository

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)

notification_repository = RedisNotificationRepository(redis_client)
event_repository = RedisNotificationEventRepository(redis_client)
notification_service = NotificationService(notification_repository, event_repository)
publisher = RabbitMQPublisher()
