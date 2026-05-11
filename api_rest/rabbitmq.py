from __future__ import annotations

import json
import logging

import pika
from django.conf import settings

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

    def publish_order_created(self, event: OrderCreatedEvent) -> None:
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
        )

        connection = pika.BlockingConnection(parameters)
        try:
            channel = connection.channel()
            channel.exchange_declare(
                exchange=self.exchange,
                exchange_type='fanout',
                durable=True,
            )
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
