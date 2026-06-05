import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Order


class OrderStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        user = self.scope.get('user')

        if not getattr(user, 'is_authenticated', False) or not hasattr(user, 'user_nickname'):
            await self.close(code=4401)
            return

        order = await self._get_order()
        if order is None:
            await self.close(code=4404)
            return

        if not getattr(user, 'is_admin', False) and order.user_id != user.user_nickname:
            await self.close(code=4403)
            return

        self.group_name = f'pedido_{self.order_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        if not hasattr(self, 'group_name'):
            return

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    @database_sync_to_async
    def _get_order(self):
        try:
            return Order.objects.select_related('user').get(pk=self.order_id)
        except Order.DoesNotExist:
            return None

    async def order_status_update(self, event):
        await self.send(text_data=json.dumps({
            'pedido_id': str(event['pedido_id']),
            'status': event['status'],
            'status_anterior': event['status_anterior'],
            'alterado_em': event['alterado_em'],
            'observacao': event.get('observacao', ''),
        }))
