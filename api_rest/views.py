from django.db import transaction
from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Cart, CartItem, Event, Order, OrderItem, User
from .serializers import (
    AddCartItemSerializer,
    CartSerializer,
    EventSerializer,
    OrderSerializer,
    UpdateCartItemSerializer,
    UserSerializer,
)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('date')
    serializer_class = EventSerializer


@api_view(['GET'])
def get_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT'])
def get_by_nick(request, nick):
    try:
        user = User.objects.get(pk=nick)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    serializer = UserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        data = serializer.data
        data.pop('password', None)
        return Response(data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    nick = request.data.get('user_nickname')
    pwd = request.data.get('password')

    if not nick or not pwd:
        return Response(
            {'error': 'Nickname e senha são obrigatórios.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(pk=nick)
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if not user.check_password(pwd):
        return Response({'error': 'Senha incorreta.'}, status=status.HTTP_400_BAD_REQUEST)

    data = {
        'user_nickname': user.user_nickname,
        'user_name': user.user_name,
        'user_email': user.user_email,
    }
    return Response(data)


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


@api_view(['GET'])
def get_cart(request, nick):
    user = _get_user_or_404(nick)
    if not user:
        return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    cart = _get_or_create_cart(user)
    return Response(CartSerializer(cart).data)


@api_view(['POST'])
def add_to_cart(request, nick):
    user = _get_user_or_404(nick)
    if not user:
        return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = AddCartItemSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    cart = _get_or_create_cart(user)
    event = serializer.validated_data['event']
    quantity = serializer.validated_data['quantity']
    cart_item = CartItem.objects.filter(cart=cart, event=event).first()
    new_quantity = quantity if cart_item is None else cart_item.quantity + quantity
    reserved = _reserved_quantity_for_event(event, cart_item.pk if cart_item else None)

    if new_quantity + reserved > event.available_tickets:
        return Response(
            {'error': 'Quantidade indisponível para este evento.'},
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
        return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    cart = _get_or_create_cart(user)
    try:
        cart_item = cart.items.get(pk=item_id)
    except CartItem.DoesNotExist:
        return Response({'error': 'Item do carrinho não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = UpdateCartItemSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    quantity = serializer.validated_data['quantity']
    reserved = _reserved_quantity_for_event(cart_item.event, cart_item.pk)
    if quantity + reserved > cart_item.event.available_tickets:
        return Response(
            {'error': 'Quantidade indisponível para este evento.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cart_item.quantity = quantity
    cart_item.save(update_fields=['quantity'])
    return Response(CartSerializer(cart).data)


@api_view(['POST'])
def checkout_cart(request, nick):
    user = _get_user_or_404(nick)
    if not user:
        return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    cart = _get_or_create_cart(user)
    items = list(cart.items.select_related('event'))
    if not items:
        return Response({'error': 'O carrinho está vazio.'}, status=status.HTTP_400_BAD_REQUEST)

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

    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def list_orders(request, nick):
    user = _get_user_or_404(nick)
    if not user:
        return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    orders = user.orders.prefetch_related('items__event').order_by('-created_at')
    return Response(OrderSerializer(orders, many=True).data)
