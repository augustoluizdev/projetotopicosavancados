# Implementacao WebSocket - Comunicacao em tempo real

Este documento registra a adaptacao da atividade de comunicacao em tempo real da Aula 10 para o ecossistema Django.

O material original usa .NET + SignalR. Como este projeto e Django/Python, a solucao equivalente foi implementada com:

- Django Channels;
- WebSockets nativos;
- Redis como channel layer/backplane;
- SimpleJWT para autenticacao por token;
- uma tela HTML simples e independente para teste no navegador.

## Objetivo

Permitir que clientes acompanhem atualizacoes de status de um pedido em tempo real, sem reload da pagina.

Fluxo esperado:

```text
Cliente abre tela do pedido
        |
        v
Browser conecta no WebSocket ws/orders/<order_id>/
        |
        v
Consumer adiciona conexao ao grupo pedido_<order_id>
        |
        v
Backend altera status do pedido
        |
        v
notifications.py dispara group_send
        |
        v
Consumer envia JSON ao browser
        |
        v
Tela atualiza status, data e observacao
```

## Arquivos principais

### `api_topicos/settings.py`

Configuracoes adicionadas ou ajustadas:

- `daphne` e `channels` em `INSTALLED_APPS`;
- `ASGI_APPLICATION = 'api_topicos.asgi.application'`;
- `CHANNEL_LAYERS` usando `channels_redis.core.RedisChannelLayer`;
- `SIMPLE_JWT` usando `user_nickname` como claim do usuario;
- configuracoes Celery com Redis;
- diretorio global de templates em `BASE_DIR / 'templates'`.

Channel layer:

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [
                (
                    os.environ.get('REDIS_HOST', '127.0.0.1'),
                    int(os.environ.get('REDIS_PORT', '6379')),
                )
            ],
        },
    },
}
```

### `api_topicos/asgi.py`

O ASGI foi configurado com:

- `ProtocolTypeRouter`;
- roteamento HTTP padrao do Django;
- roteamento WebSocket;
- `JWTAuthMiddleware`;
- `URLRouter` com as rotas de `api_rest.routing`.

### `api_rest/channels_middleware.py`

Middleware customizado `JWTAuthMiddleware`.

Responsabilidades:

- ler o parametro `token` da query string;
- validar o token com SimpleJWT;
- procurar o usuario pelo `user_nickname`, `user_id`, `sub` ou `username`;
- associar o usuario validado em `scope["user"]`;
- usar `AnonymousUser` quando nao houver token valido.

Exemplo de conexao:

```text
ws://localhost:8000/ws/orders/1/?token=TOKEN_ACCESS
```

### `api_rest/routing.py`

Rota WebSocket:

```python
websocket_urlpatterns = [
    re_path(r'ws/orders/(?P<order_id>\w+)/$', OrderStatusConsumer.as_asgi()),
]
```

### `api_rest/consumers.py`

Consumer `OrderStatusConsumer`.

Comportamento:

- recebe `order_id` pela URL;
- cria o grupo `pedido_<order_id>`;
- adiciona o canal atual ao grupo no `connect`;
- remove no `disconnect`;
- envia ao cliente o payload JSON recebido pelo evento `order_status_update`.

### `api_rest/notifications.py`

Centraliza o disparo de notificacoes em tempo real.

Funcao principal:

```python
broadcast_order_status_update(
    order_id,
    status,
    status_anterior,
    alterado_em=None,
    observacao='',
)
```

Payload entregue ao frontend:

```json
{
  "pedido_id": "1",
  "status": "notification_sent",
  "status_anterior": "requested",
  "alterado_em": "2026-05-20T02:59:45.000000+00:00",
  "observacao": "Notificacao enviada ao cliente."
}
```

### `templates/detalhe_pedido.html`

Tela de teste independente, sem Angular.

Recursos:

- Tailwind CSS via CDN;
- banner de conexao;
- card com status do pedido;
- WebSocket nativo;
- leitura de token por query string ou `localStorage`;
- reconexao automatica com exponential backoff;
- atualizacao reativa do DOM.

URL:

```text
http://localhost:8000/api/orders/<order_id>/detalhe/?token=TOKEN_ACCESS
```

### `api_rest/tests/test_websockets.py`

Teste automatizado com:

- `pytest`;
- `channels.testing.WebsocketCommunicator`;
- `channel_layer.group_send`;
- assert do payload JSON recebido pelo consumer.

Comando:

```bash
docker compose exec web pytest api_rest/tests/test_websockets.py
```

## Infraestrutura Docker

Servicos envolvidos:

| Servico | Uso |
|---------|-----|
| `web` | Django, DRF, Daphne e Channels |
| `redis` | Channel layer do Channels e broker do Celery |
| `worker` | Celery worker |
| `db` | PostgreSQL |
| `rabbitmq` | Mensageria disponivel para o projeto |

O `web` roda migrations automaticamente no `entrypoint.sh`.

O `worker` usa:

```yaml
SKIP_MIGRATIONS: "True"
```

Isso evita corrida entre `web` e `worker` tentando criar/aplicar migrations ao mesmo tempo.

## Variaveis de ambiente

Arquivo `.env` esperado:

```env
SECRET_KEY=django-insecure-dev-websocket-local-only-change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,web

DB_ENGINE=django.db.backends.postgresql
DB_NAME=api_topicos_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_ORDER_CREATED_EXCHANGE=orders
RABBITMQ_ORDER_CREATED_ROUTING_KEY=order.created
RABBITMQ_ORDER_CREATED_QUEUE=order.created.notifications
```

## Como validar manualmente

### 1. Subir o ambiente

```bash
docker compose up --build -d
```

### 2. Conferir containers

```bash
docker compose ps
```

Esperado:

- `web` up;
- `worker` up;
- `db` healthy;
- `redis` healthy;
- `rabbitmq` healthy.

### 3. Cadastrar usuario

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_nickname": "cliente1",
    "user_name": "Cliente Teste",
    "user_email": "cliente1@email.com",
    "user_age": 25,
    "password": "123456"
  }'
```

### 4. Fazer login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_nickname": "cliente1",
    "password": "123456"
  }'
```

Copie o campo `access`.

### 5. Abrir tela de pedido

```text
http://localhost:8000/api/orders/1/detalhe/?token=TOKEN_ACCESS
```

Se o banner mostrar `Tempo real ativo`, a conexao WebSocket abriu corretamente.

### 6. Rodar teste automatizado

```bash
docker compose exec web pytest api_rest/tests/test_websockets.py
```

Resultado esperado:

```text
1 passed
```

## Status atual

Implementado:

- WebSocket por pedido;
- grupos por pedido no Channels;
- middleware JWT;
- Redis channel layer;
- payload padronizado;
- tela HTML reativa;
- reconexao automatica;
- teste de integracao;
- Docker com `web`, `worker`, `db`, `redis` e `rabbitmq`.

Pontos que podem evoluir:

- exigir autenticacao obrigatoria no WebSocket em vez de permitir anonimo;
- verificar se o usuario conectado tem permissao para acessar o pedido;
- adicionar logs estruturados para eventos WebSocket;
- criar testes de permissao/autorizacao;
- trocar a tela de teste por um frontend oficial, caso o projeto adote Angular ou React.
