# Aqui definimos os serializers, que são responsáveis por converter os objetos do modelo em formatos que podem ser facilmente renderizados em JSON, XML, etc. Eles também são usados para validar os dados de entrada.

from rest_framework import serializers

from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

