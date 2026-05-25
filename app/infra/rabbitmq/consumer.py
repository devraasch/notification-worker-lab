import json
import logging
from typing import Callable

import pika

from app.config.settings import settings

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    def __init__(self, on_message: Callable[[dict], None]):
        self._on_message = on_message
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

    def _callback(self, ch, method, properties, body: bytes) -> None:
        try:
            message = json.loads(body)
            logger.info("Mensagem recebida: %s", message)
            self._on_message(message)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            logger.exception("Erro ao processar mensagem")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start(self) -> None:
        self._connect()
        self._channel.basic_qos(prefetch_count=1)
        self._channel.basic_consume(
            queue=settings.rabbitmq_queue,
            on_message_callback=self._callback,
        )
        logger.info("Worker aguardando mensagens na fila '%s'...", settings.rabbitmq_queue)
        self._channel.start_consuming()

    def stop(self) -> None:
        if self._channel:
            self._channel.stop_consuming()
        if self._connection and not self._connection.is_closed:
            self._connection.close()
