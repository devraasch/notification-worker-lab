import json
import logging

import pika

from app.config.settings import settings

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    def __init__(self):
        self._connection: pika.BlockingConnection | None = None
        self._channel: pika.adapters.blocking_connection.BlockingChannel | None = None

    def _connect(self) -> None:
        credentials = pika.PlainCredentials(
            settings.rabbitmq_username,
            settings.rabbitmq_password,
        )
        parameters = pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            virtual_host=settings.rabbitmq_vhost,
            credentials=credentials,
        )
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()

        self._channel.exchange_declare(
            exchange=settings.rabbitmq_exchange,
            exchange_type="direct",
            durable=True,
        )
        self._channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
        self._channel.queue_bind(
            queue=settings.rabbitmq_queue,
            exchange=settings.rabbitmq_exchange,
            routing_key=settings.rabbitmq_routing_key,
        )

    def publish(self, message: dict) -> None:
        try:
            if self._connection is None or self._connection.is_closed:
                self._connect()

            self._channel.basic_publish(
                exchange=settings.rabbitmq_exchange,
                routing_key=settings.rabbitmq_routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent,
                    content_type="application/json",
                ),
            )
            logger.info("Mensagem publicada: %s", message)
        except Exception:
            logger.exception("Erro ao publicar mensagem")
            raise

    def close(self) -> None:
        if self._connection and not self._connection.is_closed:
            self._connection.close()
