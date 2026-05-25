from app.application.dto.create_notification_input import CreateNotificationInput
from app.application.dto.create_notification_output import CreateNotificationOutput
from app.domain.services.notification_service import NotificationService
from app.infra.rabbitmq.publisher import RabbitMQPublisher


class CreateNotificationUseCase:
    def __init__(
        self,
        notification_service: NotificationService,
        publisher: RabbitMQPublisher,
    ):
        self.notification_service = notification_service
        self.publisher = publisher

    def execute(self, input: CreateNotificationInput) -> CreateNotificationOutput:
        notification = self.notification_service.create_notification(
            title=input.title,
            message=input.message,
        )

        self.publisher.publish({"notification_id": notification.id})

        return CreateNotificationOutput(
            id=notification.id,
            title=notification.title,
            message=notification.message,
            status=notification.status.value,
            created_at=notification.created_at,
        )
