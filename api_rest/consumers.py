import json

from channels.generic.websocket import AsyncWebsocketConsumer


class OrderStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.group_name = f'pedido_{self.order_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    async def order_status_update(self, event):
        await self.send(text_data=json.dumps({
            'pedido_id': str(event['pedido_id']),
            'status': event['status'],
            'status_anterior': event['status_anterior'],
            'alterado_em': event['alterado_em'],
            'observacao': event.get('observacao', ''),
        }))
