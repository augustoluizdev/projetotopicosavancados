import pytest
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.test import override_settings
from django.utils import timezone

from api_topicos.asgi import application


TEST_CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}


@pytest.mark.asyncio
@override_settings(CHANNEL_LAYERS=TEST_CHANNEL_LAYERS)
async def test_assinar_pedido_deve_receber_notificacao_status_atualizado():
    pedido_id = '123'
    communicator = WebsocketCommunicator(application, f'/ws/orders/{pedido_id}/')

    try:
        connected, _ = await communicator.connect(timeout=5)
        assert connected

        payload = {
            'pedido_id': pedido_id,
            'status': 'notification_sent',
            'status_anterior': 'requested',
            'alterado_em': timezone.now().isoformat(),
            'observacao': 'Status atualizado durante o teste.',
        }
        channel_layer = get_channel_layer()

        await channel_layer.group_send(
            f'pedido_{pedido_id}',
            {
                'type': 'order_status_update',
                **payload,
            },
        )

        response = await communicator.receive_json_from(timeout=5)

        assert response == payload
    finally:
        await communicator.disconnect()
