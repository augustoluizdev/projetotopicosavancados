# Aqui ficam as views da nossa API. As views são responsáveis por receber as requisições, processá-las e retornar uma resposta. Elas são o coração da nossa API, onde a lógica de negócio é implementada.

from urllib import request

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import User
from .serializers import UserSerializer

import json

# Aqui ficam as views da nossa API. As views são responsáveis por receber as requisições, processá-las e retornar uma resposta. Elas são o coração da nossa API, onde a lógica de negócio é implementada.

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


