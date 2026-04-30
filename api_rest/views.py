from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import User, Event
from .serializers import UserSerializer, EventSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'user_nickname'
    lookup_url_kwarg = 'nick'

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            data.pop('password', None)
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        nick = request.data.get('user_nickname')
        pwd = request.data.get('password')
        if not nick or not pwd:
            return Response({'error': 'Nickname e senha são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(user_nickname=nick)
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(pwd):
            return Response({'error': 'Senha incorreta.'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'user_nickname': user.user_nickname,
            'user_name': user.user_name,
            'user_email': user.user_email,
            'user_age': user.user_age,
        }
        return Response(data, status=status.HTTP_200_OK)
