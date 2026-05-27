# projetotopicosavancados

API REST para gerenciamento de usuarios, eventos, carrinho e pedidos, construida com Django, Django REST Framework, PostgreSQL, RabbitMQ e WebSocket.

## Requisitos

- Docker Desktop
- Docker Compose
- Git
- Opcional: Postman, Insomnia ou curl para testar a API

## Como rodar com Docker

```bash
docker compose up --build
```

Apos subir os containers, acesse:

| Servico | URL |
|---------|-----|
| Django API | http://localhost:8000/api/ |
| Admin Django | http://localhost:8000/admin/ |
| Health check | http://localhost:8000/health/ |
| Metricas Prometheus do Django | http://localhost:8000/metrics |
| Prometheus | http://localhost:9090/ |
| Grafana | http://localhost:3000/ |
| RabbitMQ Management | http://localhost:15672/ |

Credenciais locais padrao:

| Servico | Usuario | Senha |
|---------|---------|-------|
| Grafana | admin | admin |
| RabbitMQ | guest | guest |

## Comandos uteis

```bash
docker compose up --build
docker compose up --build -d
docker compose down
docker compose down -v
docker compose logs -f web
docker compose logs -f worker
docker compose exec web python manage.py test
docker compose exec web python manage.py createsuperuser
```

## Variaveis de ambiente

O projeto le variaveis do arquivo `.env` e do `docker-compose.yml`.

| Variavel | Descricao | Padrao |
|----------|-----------|--------|
| `SECRET_KEY` | Chave secreta do Django | `django-insecure-dev-key-change-in-production` |
| `DEBUG` | Liga/desliga debug | `True` |
| `ALLOWED_HOSTS` | Hosts aceitos pelo Django | `localhost,127.0.0.1` |
| `LOG_LEVEL` | Nivel dos logs da aplicacao | `INFO` |
| `DB_ENGINE` | Backend do banco | `django.db.backends.postgresql` |
| `DB_NAME` | Nome do banco | `api_topicos_db` |
| `DB_USER` | Usuario do banco | `postgres` |
| `DB_PASSWORD` | Senha do banco | `postgres123` |
| `DB_HOST` | Host do banco | `db` |
| `DB_PORT` | Porta do banco | `5432` |
| `CACHE_URL` | URL do Redis usado pelo cache do Django | `redis://redis:6379/1` no Docker |
| `RABBITMQ_HOST` | Host do RabbitMQ | `rabbitmq` |
| `RABBITMQ_PORT` | Porta do RabbitMQ | `5672` |
| `RABBITMQ_USER` | Usuario do RabbitMQ | `guest` |
| `RABBITMQ_PASSWORD` | Senha do RabbitMQ | `guest` |
| `RABBITMQ_RETRY_ATTEMPTS` | Tentativas para publicar evento no RabbitMQ | `3` |
| `RABBITMQ_RETRY_WAIT_SECONDS` | Espera entre tentativas | `0.5` |

## Endpoints principais

### Usuarios

| Metodo | URL | Descricao |
|--------|-----|-----------|
| GET | `/api/users/` | Lista usuarios |
| POST | `/api/auth/register/` | Cria usuario |
| POST | `/api/auth/login/` | Login simples |
| GET | `/api/users/<nick>/` | Busca usuario |
| PUT | `/api/users/<nick>/` | Atualiza usuario |
| DELETE | `/api/users/<nick>/` | Remove usuario |

### Eventos

| Metodo | URL | Descricao |
|--------|-----|-----------|
| GET | `/api/events/` | Lista eventos |
| POST | `/api/events/` | Cria evento |
| GET | `/api/events/<id>/` | Busca evento |
| PUT/PATCH | `/api/events/<id>/` | Atualiza evento |
| DELETE | `/api/events/<id>/` | Remove evento |

### Carrinho e pedidos

| Metodo | URL | Descricao |
|--------|-----|-----------|
| GET | `/api/cart/<nick>/` | Consulta carrinho |
| POST | `/api/cart/<nick>/items/` | Adiciona item ao carrinho |
| PUT/DELETE | `/api/cart/<nick>/items/<item_id>/` | Atualiza ou remove item |
| POST | `/api/cart/<nick>/checkout/` | Cria pedido |
| GET | `/api/orders/<nick>/` | Lista pedidos do usuario |
| GET | `/api/orders/<order_id>/status/` | Consulta status do pedido |

## Observabilidade e resiliencia

Esta implementacao usa tecnologias compativeis com Python/Django:

- Python Logging: logs no console para criacao, atualizacao, remocao, login, carrinho, checkout, publicacao e consumo de eventos.
- django-health-check: endpoint `/health/` validando aplicacao, banco, cache e RabbitMQ.
- django-prometheus: endpoint `/metrics` com metricas do Django para Prometheus.
- Prometheus: servico no Docker Compose coletando `web:8000/metrics`.
- Grafana: servico no Docker Compose com datasource Prometheus provisionado.
- Redis: cache do Django no Docker, usado pelas consultas de eventos.
- Tenacity: retry limitado na publicacao de eventos de pedido no RabbitMQ.

## Como validar

Com os containers rodando:

```bash
curl http://localhost:8000/health/
curl http://localhost:8000/metrics
curl http://localhost:9090/-/ready
```

Para rodar os testes:

```bash
docker compose exec web python manage.py test
```

## O que foi implementado nesta etapa

- Configuracao de `django-health-check` e endpoint `/health/`.
- Configuracao de `django-prometheus` e endpoint `/metrics`.
- Servicos `redis`, `prometheus` e `grafana` no `docker-compose.yml`, sem duplicar `postgres`, `redis`, `rabbitmq`, `prometheus` ou `grafana`.
- Arquivo `prometheus.yml` para coletar metricas do Django.
- Datasource do Grafana apontando para o Prometheus.
- Cache Django via Redis no Docker, com fallback local em ambiente sem `CACHE_URL`.
- Health check customizado para RabbitMQ.
- Retry com Tenacity na publicacao de `OrderCreatedEvent`.
- Logs adicionais em operacoes importantes da API.
- Testes para `/health/`, `/metrics` e retry do RabbitMQ.
- Correcao do retorno dos comandos de usuario para bater com o uso feito nas views.
- Resolucao do conflito textual que existia no README.

## Pendencias para o ultimo integrante

Deixar propositalmente para o ultimo integrante:

- Melhorar o dashboard do Grafana.
- Criar ou importar um dashboard mais completo com metricas de requisicoes, tempo de resposta, erros HTTP e uso da aplicacao.
- Adicionar prints ou instrucoes finais no README mostrando como acessar e validar o Grafana.
- Fazer pequenos ajustes finais de documentacao e validacao antes do commit final.

## Troubleshooting

Se o banco ou cache estiverem com dados antigos:

```bash
docker compose down -v
docker compose up --build
```

Se a porta `3000` ja estiver em uso, altere a porta do Grafana no `docker-compose.yml`, por exemplo:

```yaml
ports:
  - "3001:3000"
```

Se o Prometheus nao conseguir coletar metricas, confirme se o alvo `django` aparece como `UP` em http://localhost:9090/targets.
