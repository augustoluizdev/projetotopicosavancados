# projetotopicosavancados

API REST em Django para gerenciamento de usuarios, eventos, carrinho e pedidos, com processamento assincrono, mensageria, observabilidade e comunicacao em tempo real.

[![CI](https://github.com/augustoluizdev/projetotopicosavancados/actions/workflows/ci.yml/badge.svg)](https://github.com/augustoluizdev/projetotopicosavancados/actions/workflows/ci.yml)
[![SonarCloud](https://sonarcloud.io/api/project_badges/measure?project=augustoluizdev_projetotopicosavancados&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=augustoluizdev_projetotopicosavancados)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=augustoluizdev_projetotopicosavancados&metric=coverage)](https://sonarcloud.io/summary/new_code?id=augustoluizdev_projetotopicosavancados)

## Visao geral

O projeto implementa:

- CRUD de usuarios.
- Autenticacao com SimpleJWT.
- Autorizacao por perfil: admin cria eventos, usuarios acessam apenas proprio perfil, carrinho e pedidos.
- CRUD de eventos com read model CQRS.
- Carrinho, checkout e pedidos.
- Publicacao de evento `OrderCreatedEvent` no RabbitMQ.
- Consumo idempotente de eventos de pedido criado.
- Notificacao de status do pedido via Django Channels/WebSocket.
- Redis como channel layer do Channels e broker/result backend do Celery.
- PostgreSQL como banco principal.
- Health checks, logs estruturados e pipeline de CI/SonarCloud.

## Arquitetura

```text
Cliente HTTP
    |
    | REST
    v
Django + DRF
    |
    | ORM
    v
PostgreSQL

Django
    |
    | Celery task
    v
Celery worker
    |
    | broker/result backend
    v
Redis

Django
    |
    | publica OrderCreatedEvent
    v
RabbitMQ
    |
    | management command consume_order_created
    v
NotificationService
    |
    | Channels group_send
    v
WebSocket ws/orders/<order_id>/
```

## Stack

- Python 3.12.
- Django 6.0.3.
- Django REST Framework 3.16.1.
- SimpleJWT.
- Django Channels, Daphne e Channels Redis.
- Celery.
- PostgreSQL 16.
- Redis 7.
- RabbitMQ 3 com Management UI.
- Docker Compose.
- GitHub Actions, Ruff, Coverage e SonarCloud.

## Estrutura

```text
projetotopicosavancados/
  api_rest/                  # Aplicacao principal da API
    commands/                # Commands de dominio
    management/commands/     # Comandos Django auxiliares
    migrations/              # Migracoes do banco
    queries/                 # Queries de leitura
    tests/                   # Testes automatizados
    cache.py                 # Servico de cache Redis para eventos
    consumers.py             # Consumer WebSocket de status de pedido
    health_checks.py         # Health, liveness e readiness
    models.py                # User, Event, Cart, Order e ProcessedEvent
    notifications.py         # Processamento e broadcast de notificacoes
    rabbitmq.py              # Publisher RabbitMQ
    read_models.py           # Read model CQRS de eventos
    serializers.py           # Serializers DRF
    urls.py                  # Rotas da aplicacao
    views.py                 # Views e viewsets
  api_topicos/               # Configuracao do projeto Django
    asgi.py                  # ASGI com HTTP e WebSocket
    celery_app.py            # Configuracao Celery
    settings.py              # Configuracoes principais
    urls.py                  # Rotas raiz
    wsgi.py                  # WSGI
  templates/
    detalhe_pedido.html      # Tela simples para acompanhar pedido em tempo real
  .github/workflows/
    ci.yml                   # Lint, checks, testes e build Docker
    sonar.yml                # Analise SonarCloud
  docker-compose.yml         # Orquestracao local
  Dockerfile                 # Imagem da aplicacao
  entrypoint.sh              # Migracoes, collectstatic e start do servico
  requirements.txt           # Dependencias Python
```

## Variaveis de ambiente

Crie um arquivo `.env` na raiz. Use `.env.example` como base.

```env
SECRET_KEY=django-insecure-dev-key-change-in-production
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
REDIS_DB=0
REDIS_PASSWORD=redissenha123
REDIS_KEY_PREFIX=api_topicos:
REDIS_ITEM_TTL_SECONDS=300
REDIS_LIST_TTL_SECONDS=120

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

## Como rodar

Com Docker:

```bash
docker compose up --build
```

A API fica disponivel em:

```text
http://localhost:8000/
```

Servicos expostos:

| Servico | URL/porta |
|---------|-----------|
| API Django | `http://localhost:8000` |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |
| RabbitMQ AMQP | `localhost:5672` |
| RabbitMQ Management | `http://localhost:15672` |

Comandos uteis:

```bash
docker compose ps
docker compose logs -f web
docker compose logs -f worker
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py test
docker compose down
docker compose down -v
```

## Como rodar localmente sem Docker

Requer Python 3.12 e servicos externos configurados ou ajustes no `.env`.

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Para Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Endpoints principais

### Autenticacao e usuarios

| Metodo | Rota | Descricao |
|--------|------|-----------|
| `POST` | `/api/auth/register/` | Cadastra usuario |
| `POST` | `/api/auth/login/` | Autentica e retorna tokens JWT |
| `Authorization` | `Bearer <access_token>` | Necessario nas rotas protegidas |
| `GET` | `/api/` | Lista usuarios pela rota legada |
| `GET` | `/api/users/` | Lista usuarios pelo router DRF |
| `GET` | `/api/user/<nick>/` | Busca usuario por nickname |
| `PUT` | `/api/user/<nick>/` | Atualiza usuario |
| `GET` | `/api/users/<nick>/` | Busca usuario pelo ViewSet |
| `PUT` | `/api/users/<nick>/` | Atualiza usuario pelo ViewSet |
| `DELETE` | `/api/users/<nick>/` | Remove usuario pelo ViewSet |

### Eventos

| Metodo | Rota | Descricao |
|--------|------|-----------|
| `GET` | `/api/events/` | Lista eventos pelo read model |
| `POST` | `/api/events/` | Cria evento e agenda atualizacao do read model |
| `GET` | `/api/events/<id>/` | Busca evento pelo read model |
| `PUT` | `/api/events/<id>/` | Atualiza evento (admin) |
| `PATCH` | `/api/events/<id>/` | Atualiza evento parcialmente (admin) |
| `DELETE` | `/api/events/<id>/` | Remove evento (admin) |

### Carrinho e pedidos

| Metodo | Rota | Descricao |
|--------|------|-----------|
| `GET` | `/api/cart/<nick>/` | Consulta carrinho do usuario autenticado |
| `POST` | `/api/cart/<nick>/items/` | Adiciona item ao carrinho do usuario autenticado |
| `PUT` | `/api/cart/<nick>/items/<item_id>/` | Atualiza quantidade do item do usuario autenticado |
| `DELETE` | `/api/cart/<nick>/items/<item_id>/` | Remove item do carrinho do usuario autenticado |
| `POST` | `/api/cart/<nick>/checkout/` | Cria pedido a partir do carrinho do usuario autenticado |
| `GET` | `/api/orders/<nick>/` | Lista pedidos do proprio usuario ou do admin |
| `GET` | `/api/orders/<order_id>/status/` | Consulta status do proprio pedido ou do admin |
| `GET` | `/api/orders/<order_id>/detalhe/` | Abre tela HTML de acompanhamento |

### Observabilidade

| Metodo | Rota | Descricao |
|--------|------|-----------|
| `GET` | `/health/` | Health completo: banco, RabbitMQ e diretorio de logs |
| `GET` | `/health/live/` | Liveness simples |
| `GET` | `/health/ready/` | Readiness: banco e RabbitMQ |
| `GET` | `/admin/` | Admin Django |

## Exemplos de uso

Cadastrar usuario:

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

Login:

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_nickname": "cliente1",
    "password": "123456"
  }'
```

Criar evento:

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

Adicionar item ao carrinho:

```bash
curl -X POST http://localhost:8000/api/cart/cliente1/items/ \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "quantity": 2
  }'
```

Fazer checkout:

```bash
curl -X POST http://localhost:8000/api/cart/cliente1/checkout/
```

## WebSocket de pedidos

O acompanhamento em tempo real usa Django Channels.

Rota WebSocket:

```text
ws://localhost:8000/ws/orders/<order_id>/?token=<ACCESS_TOKEN>
```

O token precisa pertencer ao dono do pedido, ou a um usuario admin.

Tela HTML de teste:

```text
http://localhost:8000/api/orders/<order_id>/detalhe/?token=<ACCESS_TOKEN>
```

Se o token nao for informado, a tela abre apenas como placeholder e nao conecta no socket.

Payload enviado ao cliente:

```json
{
  "pedido_id": "1",
  "status": "notification_sent",
  "status_anterior": "requested",
  "alterado_em": "2026-06-02T12:00:00+00:00",
  "observacao": "Notificacao enviada ao cliente."
}
```

## Mensageria e processamento assincrono

No checkout, a API cria o pedido e publica um `OrderCreatedEvent` no RabbitMQ depois do commit da transacao.

O processamento da fila e feito pelo comando:

```bash
docker compose exec web python manage.py consume_order_created
```

O consumer:

- le mensagens da fila `order.created.notifications`;
- usa `ProcessedEvent` para descartar duplicidades;
- atualiza `status_notificacao` e `data_processamento` do pedido;
- transmite a atualizacao para clientes WebSocket conectados ao grupo do pedido.

O read model de eventos pode ser reconstruido com:

```bash
docker compose exec web python manage.py rebuild_read_model
```

## Testes e qualidade

Rodar testes Django:

```bash
python manage.py test
```

Rodar teste WebSocket com pytest:

```bash
pytest api_rest/tests/test_websockets.py
```

Rodar com cobertura:

```bash
python -m coverage run --source=api_rest,api_topicos manage.py test
python -m coverage xml -o coverage.xml
```

Pipeline atual:

- `.github/workflows/ci.yml`: instala dependencias, roda Ruff, `manage.py check`, testes com coverage e build Docker.
- `.github/workflows/sonar.yml`: gera coverage e envia analise ao SonarCloud.

Para o SonarCloud funcionar, configure o secret `SONAR_TOKEN` no GitHub Actions.

## Troubleshooting

### Porta 8000 em uso

```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

Ou altere o mapeamento de porta do servico `web` no `docker-compose.yml`.

### Banco, Redis ou RabbitMQ nao sobem

```bash
docker compose down
docker compose up --build
```

Para recriar volumes:

```bash
docker compose down -v
docker compose up --build
```

### Read model vazio apos criar eventos

Verifique se o worker esta ativo:

```bash
docker compose ps
docker compose logs -f worker
```

Depois, se necessario:

```bash
docker compose exec web python manage.py rebuild_read_model
```

### WebSocket nao conecta

- Confirme se o Redis esta healthy.
- Confirme se a URL usa `/ws/orders/<order_id>/`.
- Se estiver usando token, gere um `access` novo via `/api/auth/login/`.
- Veja os logs do `web`:

```bash
docker compose logs -f web
```
