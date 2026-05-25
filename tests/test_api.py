from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(notification_service, mock_publisher):
    with (
        patch("app.presentation.api.dependencies.notification_service", notification_service),
        patch("app.presentation.api.dependencies.publisher", mock_publisher),
        patch("app.presentation.api.routes.notifications.notification_service", notification_service),
        patch("app.presentation.api.routes.notifications.publisher", mock_publisher),
    ):
        from app.main import app

        yield TestClient(app)


class TestHealthEndpoint:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestCreateNotificationEndpoint:
    def test_create(self, client):
        resp = client.post(
            "/api/notifications/",
            json={"title": "Teste", "message": "Mensagem"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Teste"
        assert data["message"] == "Mensagem"
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data

    def test_create_missing_title(self, client):
        resp = client.post(
            "/api/notifications/",
            json={"message": "Mensagem"},
        )
        assert resp.status_code == 422

    def test_create_missing_message(self, client):
        resp = client.post(
            "/api/notifications/",
            json={"title": "Titulo"},
        )
        assert resp.status_code == 422

    def test_create_empty_body(self, client):
        resp = client.post("/api/notifications/", json={})
        assert resp.status_code == 422


class TestGetNotificationEndpoint:
    def test_get_existing(self, client):
        create_resp = client.post(
            "/api/notifications/",
            json={"title": "T", "message": "M"},
        )
        nid = create_resp.json()["id"]

        resp = client.get(f"/api/notifications/{nid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == nid

    def test_get_not_found(self, client):
        resp = client.get("/api/notifications/nonexistent-id")
        assert resp.status_code == 404


class TestGetAllNotificationsEndpoint:
    def test_get_all_empty(self, client):
        resp = client.get("/api/notifications/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_all_with_data(self, client):
        client.post("/api/notifications/", json={"title": "A", "message": "1"})
        client.post("/api/notifications/", json={"title": "B", "message": "2"})

        resp = client.get("/api/notifications/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestGetByStatusEndpoint:
    def test_filter_by_status(self, client, notification_service):
        create_resp = client.post(
            "/api/notifications/", json={"title": "A", "message": "1"}
        )
        nid = create_resp.json()["id"]
        notification_service.mark_as_sent(nid)

        resp = client.get("/api/notifications/status/sent")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["status"] == "sent"


class TestEventsEndpoint:
    def test_get_events(self, client, notification_service):
        create_resp = client.post(
            "/api/notifications/", json={"title": "T", "message": "M"}
        )
        nid = create_resp.json()["id"]
        notification_service.mark_as_processing(nid)
        notification_service.mark_as_sent(nid)

        resp = client.get(f"/api/notifications/{nid}/events")
        assert resp.status_code == 200
        events = resp.json()
        assert len(events) == 3
        assert events[0]["event_type"] == "notification.created"
        assert events[1]["event_type"] == "notification.processing"
        assert events[2]["event_type"] == "notification.sent"
        assert all("event_version" in e for e in events)

    def test_get_events_not_found(self, client):
        resp = client.get("/api/notifications/nonexistent/events")
        assert resp.status_code == 404
