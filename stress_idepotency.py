import json
import sys
import time
from collections import Counter

import pika
import requests

API_URL = "http://localhost:8000/api/notifications"
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_USERNAME = "guest"
RABBITMQ_PASSWORD = "guest"
RABBITMQ_EXCHANGE = "notifications_exchange"
RABBITMQ_ROUTING_KEY = "notification.created"


def create_notification() -> str:
    response = requests.post(
        f"{API_URL}/",
        json={
            "title": "Teste RabbitMQ Idempotência",
            "message": "A mesma mensagem será publicada várias vezes",
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["id"]


def publish_duplicate_messages(notification_id: str, total: int = 100) -> Counter:
    credentials = pika.PlainCredentials(
        RABBITMQ_USERNAME,
        RABBITMQ_PASSWORD,
    )

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
        )
    )

    channel = connection.channel()

    results = Counter()

    payload = {
        "notification_id": notification_id,
    }

    for _ in range(total):
        channel.basic_publish(
            exchange=RABBITMQ_EXCHANGE,
            routing_key=RABBITMQ_ROUTING_KEY,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
            ),
        )
        results["published"] += 1

    connection.close()

    return results


def get_notification(notification_id: str) -> dict:
    response = requests.get(
        f"{API_URL}/{notification_id}",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 100

    notification_id = create_notification()

    print(f"Notification criada: {notification_id}")
    print(f"Publicando {total} mensagens duplicadas no RabbitMQ...")

    results = publish_duplicate_messages(notification_id, total)

    print("Resultado da publicação:")
    print(results)

    print("Aguardando worker processar...")
    time.sleep(5)

    notification = get_notification(notification_id)

    print("Resultado final:")
    print(notification)


if __name__ == "__main__":
    main()