from rest_framework import serializers

from .models import User, Event

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
    class Meta:
        model = Event
        fields = '__all__'