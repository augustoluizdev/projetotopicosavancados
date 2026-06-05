import pytest
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.test import override_settings
from django.utils import timezone

from api_topicos.asgi import application
from api_rest.models import Event, Order, User
from rest_framework_simplejwt.tokens import RefreshToken


TEST_CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@override_settings(CHANNEL_LAYERS=TEST_CHANNEL_LAYERS)
async def test_assinar_pedido_deve_receber_notificacao_status_atualizado():
    @database_sync_to_async
    def create_order_fixture():
        user = User.objects.create(
            user_nickname='socketbuyer',
            user_name='Socket Buyer',
            user_email='socketbuyer@example.com',
            user_age=29,
            password='hashed-password',
        )
        event = Event.objects.create(
            title='Websocket Event',
            description='Evento para teste websocket',
            date=timezone.now(),
            location='Online',
            address='Internet',
            max_participants=10,
        )
        order = Order.objects.create(user=user)
        order.items.create(event=event, quantity=1)
        return user, order

    user, order = await create_order_fixture()
    token = str(RefreshToken.for_user(user).access_token)
    communicator = WebsocketCommunicator(application, f'/ws/orders/{order.id}/?token={token}')

    try:
        connected, _ = await communicator.connect(timeout=5)
        assert connected

        payload = {
            'pedido_id': str(order.id),
            'status': 'notification_sent',
            'status_anterior': 'requested',
            'alterado_em': timezone.now().isoformat(),
            'observacao': 'Status atualizado durante o teste.',
        }
        channel_layer = get_channel_layer()

        await channel_layer.group_send(
            f'pedido_{order.id}',
            {
                'type': 'order_status_update',
                **payload,
            },
        )

        response = await communicator.receive_json_from(timeout=5)

        assert response == payload
    finally:
        await communicator.disconnect()
