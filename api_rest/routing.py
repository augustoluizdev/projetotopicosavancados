
from django.urls import re_path

from api_rest.consumers import OrderStatusConsumer

websocket_urlpatterns = [
    re_path(r'ws/orders/(?P<order_id>\\w+)/$', OrderStatusConsumer.as_asgi()),
]
