# projetotopicosavancados

API REST para gerenciamento de usuarios, eventos, carrinho, pedidos e notificacoes, construida com Django 6.0.3 e Django REST Framework 3.16.1.

[![CI](https://github.com/augustoluizdev/projetotopicosavancados/actions/workflows/ci.yml/badge.svg)](https://github.com/augustoluizdev/projetotopicosavancados/actions/workflows/ci.yml)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=augustoluizdev_projetotopicosavancados&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=augustoluizdev_projetotopicosavancados)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=augustoluizdev_projetotopicosavancados&metric=coverage)](https://sonarcloud.io/summary/new_code?id=augustoluizdev_projetotopicosavancados)

## Stack

- Django 6.0.3
- Django REST Framework 3.16.1
- PostgreSQL 16
- Redis 7
- RabbitMQ 3
- Docker e Docker Compose
- GitHub Actions

## Requisitos

- Docker Desktop
- Git
- Python 3.12, se quiser rodar fora do Docker

## Como rodar com Docker

```bash
git clone https://github.com/augustoluizdev/projetotopicosavancados.git
cd projetotopicosavancados
docker compose up --build
```

Depois disso, a API fica disponivel em `http://localhost:8000/api/`.

### Comandos uteis

- `docker compose up --build`
- `docker compose up --build -d`
- `docker compose down`
- `docker compose down -v`
- `docker compose logs -f web`
- `docker compose exec web python manage.py test`
- `docker compose exec web python manage.py createsuperuser`

## Como rodar sem Docker

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Se quiser usar SQLite localmente, configure `DB_ENGINE=django.db.backends.sqlite3` e `DB_NAME=db.sqlite3` no `.env`.

## Variaveis de ambiente

| Variavel | Descricao | Padrao |
| --- | --- | --- |
| `SECRET_KEY` | Chave secreta do Django | `django-insecure-dev-key-change-in-production` |
| `DEBUG` | Modo debug | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |
| `DB_ENGINE` | Engine do banco | `django.db.backends.postgresql` |
| `DB_NAME` | Nome do banco | `api_topicos_db` |
| `DB_USER` | Usuario do banco | `postgres` |
| `DB_PASSWORD` | Senha do banco | `postgres123` |
| `DB_HOST` | Host do banco | `db` |
| `DB_PORT` | Porta do banco | `5432` |
| `RABBITMQ_HOST` | Host do RabbitMQ | `rabbitmq` |
| `RABBITMQ_PORT` | Porta do RabbitMQ | `5672` |
| `RABBITMQ_USER` | Usuario do RabbitMQ | `guest` |
| `RABBITMQ_PASSWORD` | Senha do RabbitMQ | `guest` |
| `REDIS_HOST` | Host do Redis | `localhost` |
| `REDIS_PORT` | Porta do Redis | `6379` |
| `REDIS_DB` | Banco do Redis | `0` |
| `REDIS_PASSWORD` | Senha do Redis | `redissenha123` |

## Endpoints da API

### Autenticacao

- `POST /api/auth/register/`
- `POST /api/auth/login/`

### Usuarios

- `GET /api/users/`
- `GET /api/users/<nick>/`
- `PUT /api/users/<nick>/`
- `DELETE /api/users/<nick>/`

### Eventos

- `GET /api/events/`
- `POST /api/events/`
- `GET /api/events/<id>/`
- `PUT /api/events/<id>/`
- `PATCH /api/events/<id>/`
- `DELETE /api/events/<id>/`

### Carrinho e pedidos

- `GET /api/cart/<nick>/`
- `POST /api/cart/<nick>/items/`
- `PUT /api/cart/<nick>/items/<item_id>/`
- `DELETE /api/cart/<nick>/items/<item_id>/`
- `POST /api/cart/<nick>/checkout/`
- `GET /api/orders/<nick>/`
- `GET /api/orders/<order_id>/status/`

### Observabilidade

- `GET /health/`
- `GET /health/live/`
- `GET /health/ready/`

## GitHub Actions

O projeto tem dois workflows em `.github/workflows/`:

- `ci.yml`: roda `backend-ci` e `docker-ci` para validar código, testes, coverage e build da imagem.
- `sonar.yml`: roda a analise do SonarCloud com o mesmo ambiente de testes e cobertura.

Os dois rodam em `push`, `pull_request` e tambem podem ser disparados manualmente com `workflow_dispatch`.

### SonarCloud

O arquivo [`sonar-project.properties`](sonar-project.properties) concentra as configuracoes da analise:

- chave do projeto
- organizacao do SonarCloud
- caminhos de cobertura
- exclusoes de arquivos gerados automaticamente

### Fluxo de branches

O fluxo recomendado e:

1. Criar uma branch para cada ajuste.
2. Abrir pull request para a branch de integracao ou para `main`.
3. Aguardar o `Backend CI`, o `Docker CI` e o `Sonar Analysis` passarem antes do merge.
4. Manter `main` como base estavel do projeto.

Se voce quiser aproximar isso da regra da apostila, proteja `main` no GitHub exigindo pelo menos:

- `CI / Backend CI`
- `CI / Sonar Analysis`

Como o projeto nao tem frontend, o job `docker-ci` cumpre o papel de validar a camada de build/infraestrutura que a apostila mostra como um job adicional.

Exemplo:

```bash
git checkout -b feature/github-actions
git push -u origin feature/github-actions
```

## Docker Compose

O `docker-compose.yml` sobe:

- `web`: Django
- `db`: PostgreSQL
- `redis`: cache
- `rabbitmq`: mensageria
- `worker`: consumidor de eventos

## Estrutura resumida

```text
projetotopicosavancados/
  .github/workflows/
  api_rest/
  api_topicos/
  Dockerfile
  docker-compose.yml
  entrypoint.sh
  manage.py
  requirements.txt
  README.md
```

## Testes

```bash
python manage.py test
```

Ou, com Docker:

```bash
docker compose exec web python manage.py test
```
