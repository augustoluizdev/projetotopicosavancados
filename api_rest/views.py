# Aqui ficam as views da nossa API. As views são responsáveis por receber as requisições, processá-las e retornar uma resposta. Elas são o coração da nossa API, onde a lógica de negócio é implementada.

from urllib import request

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Cart, CartItem, Event, Order, OrderItem, User
from .serializers import (
    AddCartItemSerializer,
    CartSerializer,
    EventSerializer,
    OrderSerializer,
    UpdateCartItemSerializer,
    UserSerializer,
)
from .commands import EventCommandService
from .read_models import EventReadModel
from .tasks import update_event_read_model

from rest_framework import viewsets
from .models import Event
from .serializers import EventSerializer

import json

class EventViewSet(viewsets.ModelViewSet):
    """ViewSet para Eventos implementando CQRS.
    - Writes (POST, PUT, PATCH, DELETE): Command Side via EventCommandService
    - Reads (GET): Query Side via EventReadModel (desnormalizado)
    """

    def list(self, request, *args, **kwargs):
        """GET /api/events/ - Usa Read Model para leitura otimizada"""
        events = EventReadModel.get_all()
        return Response(events)

    def retrieve(self, request, *args, **kwargs):
        """GET /api/events/<id>/ - Busca no Read Model"""
        event = EventReadModel.get_by_id(kwargs.get('pk'))
        if not event:
            return Response({'error': 'Evento nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(event)

    def create(self, request, *args, **kwargs):
        """POST /api/events/ - Command Side: cria via Command Service e dispara task assincrona"""
        serializer = EventSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Command Side: salva no banco de escrita via Command Service
        event = EventCommandService.create_event(serializer.validated_data)

        # Dispara task assincrona para atualizar Read Model (CQRS + Eventual Consistency)
        update_event_read_model.delay(event.id)

        # Headers informando sobre consistencia eventual
        headers = {
            'X-Consistency': 'eventual',
            'X-Read-Model-Delay': '100ms',
            'Warning': 'Os dados podem levar alguns milissegundos para aparecer na listagem'
        }

        return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """PUT /api/events/<id>/ - Atualiza via Command Service"""
        event = EventCommandService.update_event(
            kwargs.get('pk'),
            request.data
        )
        update_event_read_model.delay(event.id)
        return Response(EventSerializer(event).data)

    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/events/<id>/"""
        event = EventCommandService.update_event(
            kwargs.get('pk'),
            request.data
        )
        update_event_read_model.delay(event.id)
        return Response(EventSerializer(event).data)

    def destroy(self, request, *args, **kwargs):
        """DELETE /api/events/<id>/"""
        EventCommandService.delete_event(kwargs.get('pk'))
        from .read_models import EventReadModel
        EventReadModel.delete(kwargs.get('pk'))
        return Response(status=status.HTTP_204_NO_CONTENT)


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

    if request.method == 'GET':

        users = User.objects.all() # RETORNA TODOS OS USUÁRIOS DO BANCO DE DADOS

        serializer = UserSerializer(users, many = True) # SERIALIZA OS DADOS DO BANCO DE DADOS PARA O FORMATO JSON

        return Response(serializer.data) # RETORNA OS DADOS SERIALIZADOS PARA O CLIENTE

    return Response(status=status.HTTP_400_BAD_REQUEST) # RETORNA UM ERRO 400 SE A REQUISIÇÃO NÃO FOR DO TIPO GET

# AQUI ESTÁ O MÉTODO DE BUSCAR POR NOME DE USUÁRIO, QUE RECEBE UM NOME DE USUÁRIO COMO PARÂMETRO E RETORNA OS DADOS DO USUÁRIO CORRESPONDENTE. ELE RETORNA UM STATUS 404 SE O USUÁRIO NÃO FOR ENCONTRADO, OU UM STATUS 202 SE O USUÁRIO FOR ENCONTRADO E OS DADOS FOREM VÁLIDOS.

@api_view(['GET', 'PUT'])
def get_by_nick(request, nick):

    try:
        user = User.objects.get(pk=nick)

    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':

        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    if request.method == 'PUT':

        serializer = UserSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
    
# INICIO DO CRUD

@api_view(['POST'])
def user_manager(request):

    try:
        if request.method == 'GET':

                user_nickname = request.GET['user']

                try:
                    user = User.objects.get(pk=user_nickname)
                except:
                    return Response(status=status.HTTP_404_NOT_FOUND)

                user = User.objects.get(pk=user_nickname)

                serializer = UserSerializer(serializer.data)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
# AQUI ESTÁ O MÉTODO DE CRIAÇÃO, QUE RECEBE OS DADOS DE UM NOVO USUÁRIO E O CRIA NO BANCO DE DADOS. ELE RETORNA UM STATUS 201 SE O USUÁRIO FOR CRIADO COM SUCESSO, OU UM STATUS 400 SE OS DADOS FOREM INVÁLIDOS.

    if request.method == 'POST':

        new_user = request.data

        serializer = UserSerializer(data=new_user)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        
# AQUI ESTÁ O MÉTODO DE ATUALIZAR, QUE RECEBE UM NOME DE USUÁRIO E OS DADOS ATUALIZADOS DO USUÁRIO, E ATUALIZA O USUÁRIO NO BANCO DE DADOS. ELE RETORNA UM STATUS 202 SE O USUÁRIO FOR ATUALIZADO COM SUCESSO, OU UM STATUS 400 SE O USUÁRIO NÃO FOR ENCONTRADO OU SE OS DADOS FOREM INVÁLIDOS.

    if request.method == 'PUT':

        nickname = request.data['user_nickname']
        
        try:
            update_user = User.objects.get(pk=nickname)
        except:
            return Response(serializer.data, status=status.HTTP_404_NOT_FOUND)

        print(request.data)

        serializer = UserSerializer(update_user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

# AQUI ESTÁ O MÉTODO DELETAR, QUE RECEBE UM NOME DE USUÁRIO E DELETA O USUÁRIO DO BANCO DE DADOS. ELE RETORNA UM STATUS 202 SE O USUÁRIO FOR DELETADO COM SUCESSO, OU UM STATUS 400 SE O USUÁRIO NÃO FOR ENCONTRADO.

    if request.method == 'DELETE':

        try:
            user_to_delete = User.objects.get(pk=request.data['user_nickname'])
            user_to_delete.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        except :
            return Response(status-status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        data = serializer.data
        data.pop('password', None)  # Remove a senha do retorno
        return Response(data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    nick = request.data.get('user_nickname')
    pwd = request.data.get('password')
    if not nick or not pwd:
        return Response({'error': 'Nickname e senha são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(pk=nick)
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)    
    if not user.check_password(pwd):
        return Response({'error': 'Senha incorreta.'}, status=status.HTTP_400_BAD_REQUEST)
    data = {'user_nickname':user.user_nickname, 'user_name': user.user_name, 'user_email': user.user_email}
    return Response(data)



# BANCO DE DADOS EM DJANGO

# def databaseEmDjango():
    
#     data = User.objects.get(pk='ismar_delicia') # RETORNA UM OBJETO

#     data = User.objects.filter(user_age='18') # FAZ UM QUERYSET

#     data = User.objects.exclude(user_age='18') # FAZ OUTRO QUERYSET

#     data.save()

#     data.delete()


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
