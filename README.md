# projetotopicosavancados

API REST em Django 6 com Django REST Framework, PostgreSQL, Redis, Celery e Django Channels para comunicacao em tempo real via WebSockets.

## Sumario

1. [Visao geral](#visao-geral)
2. [Arquitetura](#arquitetura)
3. [Requisitos](#requisitos)
4. [Configuracao do ambiente](#configuracao-do-ambiente)
5. [Como rodar com Docker](#como-rodar-com-docker)
6. [Como testar se funcionou](#como-testar-se-funcionou)
7. [Endpoints principais](#endpoints-principais)
8. [Fluxo WebSocket de pedidos](#fluxo-websocket-de-pedidos)
9. [Testes automatizados](#testes-automatizados)
10. [Estrutura do projeto](#estrutura-do-projeto)
11. [Troubleshooting](#troubleshooting)

## Visao geral

O projeto implementa:

- CRUD de usuarios.
- CRUD de eventos com read model assincrono via Celery.
- Fluxo de carrinho e pedidos.
- Autenticacao simples com retorno de tokens JWT via SimpleJWT.
- Comunicacao em tempo real por pedido usando Django Channels.
- Redis como backplane do Channels e broker/result backend do Celery.
- PostgreSQL como banco principal.
- RabbitMQ disponivel no ambiente para mensageria da aplicacao.

## Arquitetura

```text
Navegador / Cliente HTTP
        |
        | HTTP / REST
        v
web: Django + DRF + Daphne
        |
        | ORM
        v
db: PostgreSQL

web: Django Channels
        |
        | grupos WebSocket / channel layer
        v
redis: Redis

web
        |
        | tasks Celery
        v
worker: Celery
        |
        | broker/result backend
        v
redis: Redis

rabbitmq: RabbitMQ Management
```

Servicos do `docker-compose.yml`:

| Servico | Funcao | Porta |
|---------|--------|-------|
| `web` | Django, DRF, Daphne, Channels | `8000` |
| `db` | PostgreSQL 16 | `5432` |
| `redis` | Channels Redis e Celery broker | `6379` |
| `rabbitmq` | RabbitMQ + painel de gerenciamento | `5672`, `15672` |
| `worker` | Celery worker | interna |

## Requisitos

- Docker Desktop rodando.
- Git.
- Postman, Insomnia ou navegador para testes manuais.

## Configuracao do ambiente

Crie um arquivo `.env` na raiz do projeto. O arquivo ja fica ignorado pelo Git.

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

## Como rodar com Docker

Na raiz do projeto:

```bash
docker compose up --build
```

Para rodar em segundo plano:

```bash
docker compose up --build -d
```

Comandos uteis:

| Comando | O que faz |
|---------|-----------|
| `docker compose ps` | Mostra o status dos containers |
| `docker compose logs -f web` | Logs do Django/Daphne |
| `docker compose logs -f worker` | Logs do Celery |
| `docker compose logs -f redis` | Logs do Redis |
| `docker compose exec web python manage.py check` | Valida configuracao Django |
| `docker compose exec web python manage.py migrate` | Roda migrations manualmente |
| `docker compose down` | Para os containers mantendo volumes |
| `docker compose down -v` | Para e apaga volumes/banco |

Observacao: o `web` roda migrations e collectstatic no entrypoint. O `worker` usa `SKIP_MIGRATIONS=True` para nao disputar migrations com o `web`.

## Como testar se funcionou

Depois de subir:

```bash
docker compose ps
```

Resultado esperado:

- `db` healthy.
- `redis` healthy.
- `rabbitmq` healthy.
- `web` up com porta `8000`.
- `worker` up.

Teste HTTP rapido:

```bash
curl http://localhost:8000/api/
```

Ou abra no navegador:

```text
http://localhost:8000/api/
```

Teste Django:

```bash
docker compose exec web python manage.py check
```

Teste WebSocket automatizado:

```bash
docker compose exec web pytest api_rest/tests/test_websockets.py
```

## Endpoints principais

### Autenticacao

| Metodo | URL | Descricao |
|--------|-----|-----------|
| `POST` | `/api/auth/register/` | Cria usuario |
| `POST` | `/api/auth/login/` | Faz login e retorna `access` e `refresh` |

Exemplo de cadastro:

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

Exemplo de login:

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_nickname": "cliente1",
    "password": "123456"
  }'
```

A resposta contem:

```json
{
  "user_nickname": "cliente1",
  "user_name": "Cliente Teste",
  "user_email": "cliente1@email.com",
  "user_age": 25,
  "access": "TOKEN_ACCESS",
  "refresh": "TOKEN_REFRESH"
}
```

### Usuarios

| Metodo | URL | Descricao |
|--------|-----|-----------|
| `GET` | `/api/` | Lista usuarios |
| `GET` | `/api/user/<nick>/` | Busca usuario |
| `PUT` | `/api/user/<nick>/` | Atualiza usuario |

### Eventos

| Metodo | URL | Descricao |
|--------|-----|-----------|
| `GET` | `/api/events/` | Lista eventos pelo read model |
| `POST` | `/api/events/` | Cria evento e dispara task Celery |
| `GET` | `/api/events/<id>/` | Busca evento pelo read model |
| `PUT` | `/api/events/<id>/` | Atualiza evento |
| `PATCH` | `/api/events/<id>/` | Atualiza parcialmente |
| `DELETE` | `/api/events/<id>/` | Remove evento |

Exemplo:

```bash
curl -X POST http://localhost:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Workshop Django",
    "description": "Aula pratica de Django REST Framework",
    "date": "2026-06-15T14:00:00Z",
    "location": "Auditorio",
    "address": "Rua Exemplo, 123",
    "max_participants": 50
  }'
```

### Carrinho e pedidos

| Metodo | URL | Descricao |
|--------|-----|-----------|
| `GET` | `/api/cart/<nick>/` | Mostra carrinho do usuario |
| `POST` | `/api/cart/<nick>/items/` | Adiciona evento ao carrinho |
| `PUT` | `/api/cart/<nick>/items/<item_id>/` | Atualiza quantidade |
| `DELETE` | `/api/cart/<nick>/items/<item_id>/` | Remove item |
| `POST` | `/api/cart/<nick>/checkout/` | Cria pedido |
| `GET` | `/api/orders/<nick>/` | Lista pedidos do usuario |
| `GET` | `/api/orders/<order_id>/status/` | Consulta status do pedido |
| `GET` | `/api/orders/<order_id>/detalhe/` | Tela HTML reativa do pedido |

Adicionar item ao carrinho:

```bash
curl -X POST http://localhost:8000/api/cart/cliente1/items/ \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "quantity": 2
  }'
```

Checkout:

```bash
curl -X POST http://localhost:8000/api/cart/cliente1/checkout/
```

## Fluxo WebSocket de pedidos

### Backend

O WebSocket usa Django Channels:

- ASGI configurado em `api_topicos/asgi.py`.
- Rotas WebSocket em `api_rest/routing.py`.
- Consumer em `api_rest/consumers.py`.
- Middleware JWT em `api_rest/channels_middleware.py`.
- Redis Channel Layer em `api_topicos/settings.py`.

Rota WebSocket:

```text
ws://localhost:8000/ws/orders/<order_id>/?token=<ACCESS_TOKEN>
```

Exemplo:

```text
ws://localhost:8000/ws/orders/1/?token=TOKEN_ACCESS
```

O token e lido da query string pelo `JWTAuthMiddleware`. Se o token for valido, o usuario e associado a `scope["user"]`. Se estiver ausente ou invalido, o middleware deixa a conexao como anonima.

### Payload de notificacao

Quando o status do pedido muda, a mensagem enviada ao grupo segue este formato:

```json
{
  "pedido_id": "1",
  "status": "notification_sent",
  "status_anterior": "requested",
  "alterado_em": "2026-05-20T02:59:45.000000+00:00",
  "observacao": "Notificacao enviada ao cliente."
}
```

### Tela no navegador

Abra:

```text
http://localhost:8000/api/orders/1/detalhe/?token=TOKEN_ACCESS
```

A tela fica em `templates/detalhe_pedido.html` e possui:

- banner de conexao em tempo real;
- card com status atual;
- data/hora da ultima alteracao;
- observacao;
- reconexao automatica com exponential backoff.

Se o banner ficar verde com `Tempo real ativo`, a conexao WebSocket foi aberta.

## Testes automatizados

Rodar todos os testes:

```bash
docker compose exec web pytest
```

Rodar somente WebSocket:

```bash
docker compose exec web pytest api_rest/tests/test_websockets.py
```

Rodar checagem Django:

```bash
docker compose exec web python manage.py check
```

## Estrutura do projeto

```text
projetotopicosavancados/
  Dockerfile
  docker-compose.yml
  entrypoint.sh
  manage.py
  requirements.txt
  README.md
  IMPLEMENTACAO_WEBSOCKET.md
  pytest.ini
  templates/
    detalhe_pedido.html
  api_topicos/
    settings.py
    urls.py
    asgi.py
    wsgi.py
    celery_app.py
  api_rest/
    models.py
    serializers.py
    views.py
    urls.py
    consumers.py
    routing.py
    channels_middleware.py
    notifications.py
    tasks.py
    read_models.py
    commands.py
    migrations/
    tests.py
    tests/
      test_websockets.py
```

## Troubleshooting

### Docker acusa `.env not found`

Crie o arquivo `.env` na raiz com o conteudo da secao [Configuracao do ambiente](#configuracao-do-ambiente).

### `web` ou `worker` nao sobem

Veja os logs:

```bash
docker compose logs --tail=120 web
docker compose logs --tail=120 worker
```

Depois valide:

```bash
docker compose ps
```

### Erro `entrypoint.sh: no such file or directory`

O `Dockerfile` deve chamar o entrypoint com `sh /app/entrypoint.sh`. O script precisa estar com final de linha LF.

### Erro de migrations concorrentes

Somente o `web` deve rodar migrations. O `worker` deve ter:

```yaml
SKIP_MIGRATIONS: "True"
```

### Porta 8000 ocupada

Altere a porta no `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"
```

Depois acesse `http://localhost:8001/api/`.

### Resetar banco local

```bash
docker compose down -v
docker compose up --build
```

Isso apaga os volumes `postgres_data`, `rabbitmq_data` e `redis_data`.
