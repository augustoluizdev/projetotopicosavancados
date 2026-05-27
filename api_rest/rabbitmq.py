from __future__ import annotations

import json
import logging

import pika
from django.conf import settings
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from .order_events import OrderCreatedEvent

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    def __init__(self) -> None:
        rabbitmq = settings.RABBITMQ
        self.host = rabbitmq['HOST']
        self.port = rabbitmq['PORT']
        self.user = rabbitmq['USER']
        self.password = rabbitmq['PASSWORD']
        self.exchange = rabbitmq['ORDER_CREATED_EXCHANGE']
        self.routing_key = rabbitmq['ORDER_CREATED_ROUTING_KEY']
        self.queue = rabbitmq['ORDER_CREATED_QUEUE']

    @retry(
        retry=retry_if_exception_type(pika.exceptions.AMQPError),
        stop=stop_after_attempt(settings.RABBITMQ_RETRY_ATTEMPTS),
        wait=wait_fixed(settings.RABBITMQ_RETRY_WAIT_SECONDS),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def publish_order_created(self, event: OrderCreatedEvent) -> None:
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            blocked_connection_timeout=5,
            socket_timeout=5,
        )

        connection = pika.BlockingConnection(parameters)
        try:
            channel = connection.channel()
            channel.exchange_declare(
                exchange=self.exchange,
                exchange_type='fanout',
                durable=True,
            )
            channel.queue_declare(queue=self.queue, durable=True)
            channel.queue_bind(exchange=self.exchange, queue=self.queue)
            channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.routing_key,
                body=json.dumps(event.to_payload()),
                properties=pika.BasicProperties(
                    content_type='application/json',
                    delivery_mode=2,
                ),
            )
        finally:
            connection.close()


def publish_order_created_event(order_event: OrderCreatedEvent) -> None:
    RabbitMQPublisher().publish_order_created(order_event)
    logger.info(
        'OrderCreatedEvent published for order %s to exchange %s',
        order_event.order_id,
        settings.RABBITMQ['ORDER_CREATED_EXCHANGE'],
    )
