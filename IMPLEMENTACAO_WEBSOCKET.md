
# Alterações implementadas — Comunicação em tempo real

## O que foi implementado

Foram implementadas as primeiras etapas equivalentes ao PDF usando a stack existente do projeto (Django), já que o material da atividade foi criado para .NET + SignalR.

Como o projeto enviado utiliza Django/Python, SignalR não pode ser integrado diretamente. A solução equivalente no ecossistema Django é o Django Channels com WebSockets.

## Arquivos alterados

### api_topicos/settings.py
Adicionado:
- channels no INSTALLED_APPS
- configuração ASGI
- CHANNEL_LAYERS
- configuração CORS

Motivo:
Permitir comunicação WebSocket em tempo real.

---

### api_topicos/asgi.py
Substituído o ASGI padrão por:
- ProtocolTypeRouter
- URLRouter
- suporte WebSocket

Motivo:
O projeto originalmente aceitava apenas HTTP.

---

### api_rest/consumers.py (NOVO)
Criado consumer WebSocket:
- conexão por pedido
- grupos por pedido
- envio de atualização em tempo real

Motivo:
Equivalente ao PedidoHub do SignalR.

---

### api_rest/routing.py (NOVO)
Criadas rotas WebSocket:
- ws/orders/<order_id>/

Motivo:
Permitir assinatura de eventos por pedido.

---

### api_rest/notifications.py
Adicionado:
- broadcast via channel_layer.group_send()

Motivo:
Quando um pedido for processado, clientes conectados recebem atualização instantânea.

## Complementos finalizados

### Backend
- autenticação JWT nos WebSockets via JWTAuthMiddleware
- Redis como channel layer/backplane
- disparo do group_send apos alteracao de status do pedido
- payload padronizado para o frontend com pedido_id, status, status_anterior, alterado_em e observacao
- teste automatizado de integracao com WebsocketCommunicator

### Frontend
O projeto enviado não contém Angular, então foi criada uma SPA leve independente em:
- templates/detalhe_pedido.html

A tela possui:
- banner de status da conexao
- card reativo com status atual, ultima alteracao e observacao
- WebSocket nativo
- reconexao automatica com exponential backoff

## Dependências necessárias

Adicionar ao requirements.txt:

channels
daphne
asgiref
channels-redis
djangorestframework-simplejwt
pytest
pytest-asyncio
pytest-django
