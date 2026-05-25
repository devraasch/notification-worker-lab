from app.application.dto.create_notification_input import CreateNotificationInput
from app.application.use_cases.create_notification import CreateNotificationUseCase
from app.application.use_cases.get_notification import (
    GetAllNotificationsByStatusUseCase,
    GetAllNotificationsUseCase,
    GetNotificationUseCase,
)
from app.domain.enums.notification_status import NotificationStatus


class TestCreateNotificationUseCase:
    def test_execute_creates_and_publishes(self, notification_service, mock_publisher):
        use_case = CreateNotificationUseCase(notification_service, mock_publisher)
        result = use_case.execute(
            CreateNotificationInput(title="Alerta", message="Disco cheio")
        )

        assert result.title == "Alerta"
        assert result.message == "Disco cheio"
        assert result.status == "pending"
        assert result.id is not None
        assert result.created_at is not None

        mock_publisher.publish.assert_called_once_with({"notification_id": result.id})

    def test_execute_persists_notification(self, notification_service, mock_publisher, notification_repo):
        use_case = CreateNotificationUseCase(notification_service, mock_publisher)
        result = use_case.execute(
            CreateNotificationInput(title="T", message="M")
        )

        saved = notification_repo.get_by_id(result.id)
        assert saved is not None


class TestGetNotificationUseCase:
    def test_execute_found(self, notification_service):
        n = notification_service.create_notification("T", "M")
        use_case = GetNotificationUseCase(notification_service)

        result = use_case.execute(n.id)
        assert result is not None
        assert result.id == n.id
        assert result.title == "T"

    def test_execute_not_found(self, notification_service):
        use_case = GetNotificationUseCase(notification_service)

        result = use_case.execute("nonexistent")
        assert result is None


class TestGetAllNotificationsUseCase:
    def test_execute_returns_all(self, notification_service):
        notification_service.create_notification("A", "1")
        notification_service.create_notification("B", "2")
        use_case = GetAllNotificationsUseCase(notification_service)

        result = use_case.execute()
        assert len(result) == 2

    def test_execute_empty(self, notification_service):
        use_case = GetAllNotificationsUseCase(notification_service)

        result = use_case.execute()
        assert result == []


class TestGetAllNotificationsByStatusUseCase:
    def test_execute_filters_by_status(self, notification_service):
        n1 = notification_service.create_notification("A", "1")
        notification_service.create_notification("B", "2")
        notification_service.mark_as_sent(n1.id)

        use_case = GetAllNotificationsByStatusUseCase(notification_service)

        sent = use_case.execute(NotificationStatus.SENT)
        assert len(sent) == 1
        assert sent[0].status == "sent"

        pending = use_case.execute(NotificationStatus.PENDING)
        assert len(pending) == 1
