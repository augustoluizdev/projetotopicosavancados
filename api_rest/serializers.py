# Aqui definimos os serializers, que são responsáveis por converter os objetos do modelo em formatos que podem ser facilmente renderizados em JSON, XML, etc. Eles também são usados para validar os dados de entrada.

from rest_framework import serializers

from .models import User

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
