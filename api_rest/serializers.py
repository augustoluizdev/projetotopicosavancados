from rest_framework import serializers

from .models import Cart, CartItem, Event, Order, OrderItem, User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=6)

    class Meta:
        model = User
        fields = ['user_nickname', 'user_name', 'user_email', 'user_age', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_user_age(self, value):
        if value < 0:
            raise serializers.ValidationError('A idade deve ser um número positivo.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'A senha é obrigatória.'})
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
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
        write_only=True
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
        fields = ['id', 'user_nickname', 'status', 'items', 'created_at']
