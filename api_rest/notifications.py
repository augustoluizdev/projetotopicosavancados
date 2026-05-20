from __future__ import annotations

import json
import logging

from django.db import IntegrityError, transaction
from django.utils import timezone

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


from .models import Order, ProcessedEvent

logger = logging.getLogger(__name__)


class NotificationService:
    def send_order_created(self, order: Order, event_id: str) -> None:
        payload = {
            'timestamp': timezone.now().isoformat(),
            'order_id': order.pk,
            'user_id': order.user_id,
            'event_id': event_id,
            'status': 'notification_sent',
        }
        logger.info(json.dumps(payload))


def process_order_created_payload(payload: dict) -> str:
    event_id = str(payload.get('event_id') or '')
    order_id = payload.get('order_id')

    if not order_id:
        raise ValueError('OrderCreatedEvent sem order_id.')

    if not event_id:
        event_id = f'order:{order_id}'

    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().select_related('user').get(pk=order_id)
            _, created = ProcessedEvent.objects.get_or_create(
                event_id=event_id,
                defaults={'order': order},
            )

            if not created:
                logger.info(
                    json.dumps(
                        {
                            'timestamp': timezone.now().isoformat(),
                            'order_id': order.pk,
                            'user_id': order.user_id,
                            'event_id': event_id,
                            'status': 'duplicate_discarded',
                        }
                    )
                )
                return 'duplicate_discarded'

            NotificationService().send_order_created(order, event_id)
            order.status_notificacao = Order.NotificationStatus.NOTIFICATION_SENT
            order.data_processamento = timezone.now()
            order.save(update_fields=['status_notificacao', 'data_processamento'])

            # Envia atualização em tempo real via WebSocket
            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                f'pedido_{order.pk}',
                {
                    'type': 'order_status_update',
                    'order_id': order.pk,
                    'status': order.status_notificacao,
                    'timestamp': timezone.now().isoformat(),
                }
            )

            return Order.NotificationStatus.NOTIFICATION_SENT
    except IntegrityError:
        logger.info(
            json.dumps(
                {
                    'timestamp': timezone.now().isoformat(),
                    'order_id': order_id,
                    'event_id': event_id,
                    'status': 'duplicate_discarded',
                }
            )
        )
        return 'duplicate_discarded'
