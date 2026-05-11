import logging

from django.db import transaction
from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem, Event, Order, OrderItem, User
from .order_events import build_order_created_event
from .rabbitmq import publish_order_created_event
from .serializers import (
    AddCartItemSerializer,
    CartSerializer,
    EventSerializer,
    OrderSerializer,
    UpdateCartItemSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    # CRUD completo de usuarios em /api/users/.
    queryset = User.objects.all().order_by('user_nickname')
    serializer_class = UserSerializer
    lookup_field = 'user_nickname'
    lookup_url_kwarg = 'nick'


class EventViewSet(viewsets.ModelViewSet):
    # CRUD completo de eventos em /api/events/.
    queryset = Event.objects.all().order_by('date')
    serializer_class = EventSerializer


class RegisterView(APIView):
    # Cadastro separado para manter uma URL clara de autenticacao.
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    # Login simples: valida nickname e senha e devolve os dados publicos do usuario.
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
        return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_users(request):
    # Rota antiga para listar usuarios; o endpoint principal e /api/users/.
    users = User.objects.all().order_by('user_nickname')
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT'])
def get_by_nick(request, nick):
    # Rota antiga para buscar ou atualizar usuario pelo nickname.
    user = _get_user_or_404(nick)
    if not user:
        return Response({'error': 'Usuario nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    serializer = UserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _get_user_or_404(nick):
    # Pequeno helper para evitar repetir try/except em todas as views por usuario.
    try:
        return User.objects.get(pk=nick)
    except User.DoesNotExist:
        return None


def _get_or_create_cart(user):
    # Garante que todo usuario tenha um carrinho antes de manipular itens.
    return Cart.objects.get_or_create(user=user)[0]


def _reserved_quantity_for_event(event, cart_item_id=None):
    # Soma ingressos que ainda estao em carrinhos para nao vender acima da lotacao.
    queryset = CartItem.objects.filter(event=event)
    if cart_item_id is not None:
        queryset = queryset.exclude(pk=cart_item_id)
    total = queryset.aggregate(total=Sum('quantity')).get('total')
    return total or 0


def _has_available_tickets(event, quantity, ignored_cart_item_id=None):
    # Verifica a capacidade considerando ingressos comprados e itens em carrinhos.
    reserved = _reserved_quantity_for_event(event, ignored_cart_item_id)
    return quantity + reserved <= event.available_tickets


@api_view(['GET'])
def get_cart(request, nick):
    # Retorna o carrinho atual do usuario, criando um vazio se ele ainda nao existir.
    user = _get_user_or_404(nick)
    if not user:
        return Response({'error': 'Usuario nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    cart = _get_or_create_cart(user)
    return Response(CartSerializer(cart).data)


@api_view(['POST'])
def add_to_cart(request, nick):
    # Adiciona um evento ao carrinho ou aumenta a quantidade se ele ja existir.
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
    # Atualiza a quantidade de um item do carrinho ou remove o item.
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
    # Transforma todos os itens do carrinho em um pedido e esvazia o carrinho.
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
    # Lista o historico de pedidos do usuario, do mais recente para o mais antigo.
    user = _get_user_or_404(nick)
    if not user:
        return Response({'error': 'Usuario nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    orders = user.orders.prefetch_related('items__event').order_by('-created_at')
    return Response(OrderSerializer(orders, many=True).data)


def _publish_order_created_event(order_event):
    try:
        publish_order_created_event(order_event)
    except Exception:
        logger.exception(
            'Failed to publish OrderCreatedEvent for order %s',
            order_event.order_id,
        )
