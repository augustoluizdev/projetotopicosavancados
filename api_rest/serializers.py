# Aqui definimos os serializers, que são responsáveis por converter os objetos do modelo em formatos que podem ser facilmente renderizados em JSON, XML, etc. Eles também são usados para validar os dados de entrada.

from rest_framework import serializers

from .models import Cart, CartItem, Event, Order, OrderItem, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_nickname', 'user_name', 'user_email', 'user_age', 'password']
        extra_kwards = {'password': {'write_only': True}}

    def create(self, validated_data):
        pwd = validated_data.pop('password', None)
        user = User(**validated_data)
        if pwd:
            user.set_password(pwd)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        pwd = validated_data.pop('password', None)
        for k,v in validated_data.items():
            setattr(instance, k, v)
        if pwd:
            instance.set_password(pwd)
        instance.save()
        return instance    
class EventSerializer(serializers.ModelSerializer):
    sold_tickets = serializers.IntegerField(read_only=True)
    available_tickets = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        source='event',
        queryset=Event.objects.all(),
        write_only=True,
    )

    class Meta:
        model = CartItem
        fields = ['id', 'event', 'event_id', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user_nickname = serializers.CharField(source='user.user_nickname', read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user_nickname', 'items', 'created_at', 'updated_at']


class AddCartItemSerializer(serializers.Serializer):
    event_id = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all(), source='event')
    quantity = serializers.IntegerField(min_value=1)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'event', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_nickname = serializers.CharField(source='user.user_nickname', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user_nickname',
            'status',
            'status_notificacao',
            'data_processamento',
            'items',
            'created_at',
        ]


class OrderStatusSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user_id', 'status_notificacao', 'data_processamento']
