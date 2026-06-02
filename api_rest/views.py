import logging

from django.conf import settings
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .commands.user_commands import update_user_command
from .models import Cart, CartItem, Event, Order, OrderItem, User
from .event_command_service import EventCommandService
from .order_events import build_order_created_event
from .queries.user_queries import get_all_users_query, get_user_by_nick_query
from .rabbitmq import publish_order_created_event
from .read_models import EventReadModel
from .serializers import (
    AddCartItemSerializer,
    CartSerializer,
    EventSerializer,
    OrderSerializer,
    OrderStatusSerializer,
    UpdateCartItemSerializer,
    UserSerializer,
)
from .tasks import update_event_read_model

logger = logging.getLogger(__name__)


def version_info(request):
    environment = 'Development' if settings.DEBUG else 'Production'
    return JsonResponse(
        {
            'version': settings.APP_VERSION,
            'environment': environment,
            'build_date': timezone.now().isoformat(),
        }
    )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('user_nickname')
    serializer_class = UserSerializer
    lookup_field = 'user_nickname'
    lookup_url_kwarg = 'nick'


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('date')
    serializer_class = EventSerializer

    def list(self, request, *args, **kwargs):
        events = EventReadModel.get_all()
        return Response(events)

    def retrieve(self, request, *args, **kwargs):
        event = EventReadModel.get_by_id(kwargs.get('pk'))
        if not event:
            return Response({'error': 'Evento nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(event)

    def create(self, request, *args, **kwargs):
        serializer = EventSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        event = EventCommandService.create_event(serializer.validated_data)
        update_event_read_model.delay(event.id)

        headers = {
            'X-Consistency': 'eventual',
            'X-Read-Model-Delay': '100ms',
            'Warning': 'Os dados podem levar alguns milissegundos para aparecer na listagem',
        }
        return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        event = EventCommandService.update_event(kwargs.get('pk'), request.data)
        update_event_read_model.delay(event.id)
        return Response(EventSerializer(event).data)

    def partial_update(self, request, *args, **kwargs):
        event = EventCommandService.update_event(kwargs.get('pk'), request.data)
        update_event_read_model.delay(event.id)
        return Response(EventSerializer(event).data)

    def destroy(self, request, *args, **kwargs):
        EventCommandService.delete_event(kwargs.get('pk'))
        EventReadModel.delete(kwargs.get('pk'))
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        nick = request.data.get('user_nickname')
        password = request.data.get('password')

        if not nick or not password:
            return Response(
                {'error': 'Nickname e senha sao obrigatorios.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=nick)
        except User.DoesNotExist:
            return Response({'error': 'Usuario nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({'error': 'Senha incorreta.'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'user_nickname': user.user_nickname,
            'user_name': user.user_name,
            'user_email': user.user_email,
            'user_age': user.user_age,
        }

        try:
            from rest_framework_simplejwt.tokens import RefreshToken
        except ImportError:
            return Response(data, status=status.HTTP_200_OK)

        refresh = RefreshToken.for_user(user)
        data.update(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        )
        return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_users(request):
    users = get_all_users_query()
    return Response(users)


@api_view(['GET', 'PUT'])
def get_by_nick(request, nick):
    user = _get_user_or_404(nick)
    if not user:
        return Response({'error': 'Usuario nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        user_data = get_user_by_nick_query(nick)
        return Response(user_data)

    result, success = update_user_command(user, request.data)
    if success:
        return Response(result, status=status.HTTP_202_ACCEPTED)
    return Response(result, status=status.HTTP_400_BAD_REQUEST)


def _get_user_or_404(nick):
    try:
        return User.objects.get(pk=nick)
    except User.DoesNotExist:
        return None


def _get_or_create_cart(user):
    return Cart.objects.get_or_create(user=user)[0]


def _reserved_quantity_for_event(event, cart_item_id=None):
    queryset = CartItem.objects.filter(event=event)
    if cart_item_id is not None:
        queryset = queryset.exclude(pk=cart_item_id)
    total = queryset.aggregate(total=Sum('quantity')).get('total')
    return total or 0


def _has_available_tickets(event, quantity, ignored_cart_item_id=None):
    reserved = _reserved_quantity_for_event(event, ignored_cart_item_id)
    return quantity + reserved <= event.available_tickets


@api_view(['GET'])
def get_cart(request, nick):
    user = _get_user_or_404(nick)
    if not user:
        return Response({'error': 'Usuario nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    cart = _get_or_create_cart(user)
    return Response(CartSerializer(cart).data)


@api_view(['POST'])
def add_to_cart(request, nick):
    user = _get_user_or_404(nick)
    if not user:
        return Response({'error': 'Usuario nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = AddCartItemSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    cart = _get_or_create_cart(user)
    event = serializer.validated_data['event']
    quantity = serializer.validated_data['quantity']
    cart_item = CartItem.objects.filter(cart=cart, event=event).first()
    new_quantity = quantity if cart_item is None else cart_item.quantity + quantity

    if not _has_available_tickets(event, new_quantity, cart_item.pk if cart_item else None):
        return Response(
            {'error': 'Quantidade indisponivel para este evento.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if cart_item is None:
        CartItem.objects.create(cart=cart, event=event, quantity=quantity)
    else:
        cart_item.quantity = new_quantity
        cart_item.save(update_fields=['quantity'])

    return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'DELETE'])
def cart_item_detail(request, nick, item_id):
    user = _get_user_or_404(nick)
    if not user:
        return Response({'error': 'Usuario nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    cart = _get_or_create_cart(user)
    try:
        cart_item = cart.items.get(pk=item_id)
    except CartItem.DoesNotExist:
        return Response({'error': 'Item do carrinho nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = UpdateCartItemSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    quantity = serializer.validated_data['quantity']
    if not _has_available_tickets(cart_item.event, quantity, cart_item.pk):
        return Response(
            {'error': 'Quantidade indisponivel para este evento.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cart_item.quantity = quantity
    cart_item.save(update_fields=['quantity'])
    return Response(CartSerializer(cart).data)


@api_view(['POST'])
def checkout_cart(request, nick):
    user = _get_user_or_404(nick)
    if not user:
        return Response({'error': 'Usuario nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    cart = _get_or_create_cart(user)
    items = list(cart.items.select_related('event'))
    if not items:
        return Response({'error': 'O carrinho esta vazio.'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        event_ids = [item.event_id for item in items]
        locked_events = {
            event.id: event
            for event in Event.objects.select_for_update().filter(id__in=event_ids)
        }

        for item in items:
            event = locked_events[item.event_id]
            if item.quantity > event.available_tickets:
                return Response(
                    {'error': f'Ingressos insuficientes para o evento "{event.title}".'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        order = Order.objects.create(user=user)
        OrderItem.objects.bulk_create(
            [
                OrderItem(order=order, event=locked_events[item.event_id], quantity=item.quantity)
                for item in items
            ]
        )
        cart.items.all().delete()
        order_event = build_order_created_event(order)
        transaction.on_commit(lambda: _publish_order_created_event(order_event))

    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def list_orders(request, nick):
    user = _get_user_or_404(nick)
    if not user:
        return Response({'error': 'Usuario nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    orders = user.orders.prefetch_related('items__event').order_by('-created_at')
    return Response(OrderSerializer(orders, many=True).data)


@api_view(['GET'])
def order_status(request, order_id):
    try:
        order = Order.objects.select_related('user').get(pk=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Pedido nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(OrderStatusSerializer(order).data)


def order_detail_page(request, order_id):
    return render(request, 'detalhe_pedido.html', {'order_id': order_id})


def _publish_order_created_event(order_event):
    try:
        publish_order_created_event(order_event)
    except Exception:
        logger.exception(
            'Failed to publish OrderCreatedEvent for order %s',
            order_event.order_id,
        )
