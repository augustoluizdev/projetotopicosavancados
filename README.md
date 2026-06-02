# projetotopicosavancados

API REST em Django 6 com Django REST Framework, PostgreSQL, Redis, Celery e Django Channels para comunicacao em tempo real via WebSockets.

[![CI](https://github.com/augustoluizdev/projetotopicosavancados/actions/workflows/ci.yml/badge.svg)](https://github.com/augustoluizdev/projetotopicosavancados/actions/workflows/ci.yml)
[![SonarCloud](https://sonarcloud.io/api/project_badges/measure?project=augustoluizdev_projetotopicosavancados&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=augustoluizdev_projetotopicosavancados)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=augustoluizdev_projetotopicosavancados&metric=coverage)](https://sonarcloud.io/summary/new_code?id=augustoluizdev_projetotopicosavancados)

## Visao geral

O projeto implementa:

- CRUD de usuarios.
- CRUD de eventos com read model assincrono via Celery.
- Fluxo de carrinho e pedidos.
- Autenticacao com retorno de tokens JWT via SimpleJWT.
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
```

## Requisitos

- Docker Desktop rodando.
- Git.
- Postman, Insomnia ou navegador para testes manuais.

## Configuracao do ambiente

Crie um arquivo `.env` na raiz do projeto:

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

```bash
docker compose up --build
```

## GitHub Actions e Sonar

O repositório tem:

- `ci.yml`: lint, check, testes com coverage e build Docker.
- `sonar.yml`: analise no SonarCloud usando `coverage.xml`.

Configure o `SONAR_TOKEN` em `Settings > Secrets and variables > Actions` no GitHub, como um repository secret.

## Fluxo WebSocket de pedidos

Rota:

```text
ws://localhost:8000/ws/orders/<order_id>/?token=<ACCESS_TOKEN>
```

Tela HTML:

```text
http://localhost:8000/api/orders/<order_id>/detalhe/
```

## Endpoints principais

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `GET /api/users/`
- `GET /api/events/`
- `GET /api/cart/<nick>/`
- `POST /api/cart/<nick>/checkout/`
- `GET /api/orders/<nick>/`
- `GET /health/`
- `GET /health/live/`
- `GET /health/ready/`

## Testes

```bash
python manage.py test
```

Ou, com cobertura:

```bash
python -m coverage run --source=api_rest,api_topicos manage.py test
python -m coverage xml -o coverage.xml
```
