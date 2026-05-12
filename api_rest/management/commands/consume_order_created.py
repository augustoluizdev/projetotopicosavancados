from __future__ import annotations

import json
import logging

import pika
from django.conf import settings
from django.core.management.base import BaseCommand

from api_rest.notifications import process_order_created_payload

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Consome eventos PedidoCriado do RabbitMQ e processa notificacoes.'

    def handle(self, *args, **options):
        rabbitmq = settings.RABBITMQ
        credentials = pika.PlainCredentials(rabbitmq['USER'], rabbitmq['PASSWORD'])
        parameters = pika.ConnectionParameters(
            host=rabbitmq['HOST'],
            port=rabbitmq['PORT'],
            credentials=credentials,
        )

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.exchange_declare(
            exchange=rabbitmq['ORDER_CREATED_EXCHANGE'],
            exchange_type='fanout',
            durable=True,
        )
        channel.queue_declare(queue=rabbitmq['ORDER_CREATED_QUEUE'], durable=True)
        channel.queue_bind(
            exchange=rabbitmq['ORDER_CREATED_EXCHANGE'],
            queue=rabbitmq['ORDER_CREATED_QUEUE'],
        )
        channel.basic_qos(prefetch_count=1)

        def callback(ch, method, properties, body):
            try:
                payload = json.loads(body.decode('utf-8'))
                result = process_order_created_payload(payload)
                logger.info('OrderCreatedEvent consumed with result %s', result)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception:
                logger.exception('Failed to process OrderCreatedEvent. Message will be requeued.')
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        channel.basic_consume(
            queue=rabbitmq['ORDER_CREATED_QUEUE'],
            on_message_callback=callback,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Consuming queue {rabbitmq['ORDER_CREATED_QUEUE']}..."
            )
        )
        channel.start_consuming()
