<<<<<<< HEAD
  # projetotopicosavancados

  API REST para gerenciamento de usurios e eventos, construda com Django 6.0.3 e Django REST Framework 3.16.1.

  ---

  ## Índice

  1. [Requisitos](#requisitos)
  2. [Como rodar com Docker](#como-rodar-com-docker)
  3. [Como rodar sem Docker](#como-rodar-sem-docker)
  4. [Endpoints da API](#endpoints-da-api)
  5. [Exemplos de uso](#exemplos-de-uso)
  6. [Variaveis de ambiente](#variaveis-de-ambiente)
  7. [Como a dockerizacao funciona](#como-a-dockerizacao-funciona)
  8. [Estrutura do projeto](#estrutura-do-projeto)
  9. [Troubleshooting](#troubleshooting)

  ---

  ## Requisitos

  | Obrigatorio | Opcional |
  |-------------|----------|
  | [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Postman ou Insomnia (para testar a API) |
  | Git | |

  Aps instalar o Docker Desktop, certifique-se que ele esta rodando (icone na bandeja do sistema).

  ---

  ## Como rodar com Docker

  ### Primeira vez

  ```bash
  # 1. Clone o repositorio
  git clone https://github.com/augustoluizdev/projetotopicosavancados.git
  cd projetotopicosavancados

  # 2. Inicie tudo (constroi a imagem e sobe os containers)
  docker-compose up --build
  ```

  A API fica disponvel em **http://localhost:8000/api/**

  ### Comandos uteis

  | Comando | O que faz |
  |---------|-----------|
  | `docker-compose up --build` | Constroi e inicia (mostra logs no terminal) |
  | `docker-compose up --build -d` | Constroi e inicia em segundo plano |
  | `docker-compose down` | Para os containers |
  | `docker-compose down -v` | Para os containers e apaga o banco de dados |
  | `docker-compose logs -f` | Mostra os logs em tempo real |
  | `docker-compose logs -f web` | Mostra so os logs do Django |
  | `docker-compose exec web python manage.py test` | Roda os testes |
  | `docker-compose exec web python manage.py createsuperuser` | Cria usuario admin |
  | `docker-compose exec web python manage.py shell` | Abre shell Python do Django |
  | `docker-compose restart` | Reinicia os containers |

  ---

  ## Como rodar sem Docker

  Requer Python 3.10+ e PostgreSQL instalados localmente.

  ```bash
  # 1. Ambiente virtual
  python -m venv venv
  .\venv\Scripts\Activate.ps1   # Windows PowerShell
  source venv/bin/activate      # Linux/macOS

  # 2. Dependencias
  pip install -r requirements.txt

  # 3. Configure o .env para apontar para seu PostgreSQL local
  #    ou altere settings.py para usar SQLite

  # 4. Migre e rode
  python manage.py migrate
  python manage.py runserver
  ```

  Para usar SQLite em vez de PostgreSQL (desenvolvimento local), altere em `api_topicos/settings.py`:

  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.sqlite3',
          'NAME': BASE_DIR / 'db.sqlite3',
      }
  }
  ```

  ---

  ## Endpoints da API

  ### Usuarios

  | Metodo | URL | Descricao | Body |
  |--------|-----|-----------|------|
  | GET | `/api/users/` | Lista todos os usuarios | - |
  | POST | `/api/auth/register/` | Cria novo usuario | ver abaixo |
  | POST | `/api/auth/login/` | Realiza login | ver abaixo |
  | GET | `/api/users/<nick>/` | Busca usuario por nickname | - |
  | PUT | `/api/users/<nick>/` | Atualiza usuario | ver abaixo |
  | DELETE | `/api/users/<nick>/` | Remove usuario | - |

  ### Eventos

  | Metodo | URL | Descricao | Body |
  |--------|-----|-----------|------|
  | GET | `/api/events/` | Lista todos os eventos | - |
  | POST | `/api/events/` | Cria novo evento | ver abaixo |
  | GET | `/api/events/<id>/` | Busca evento por ID | - |
  | PUT | `/api/events/<id>/` | Atualiza evento completo | ver abaixo |
  | PATCH | `/api/events/<id>/` | Atualiza evento parcialmente | qualquer campo |
  | DELETE | `/api/events/<id>/` | Deleta evento | - |

  ### Admin

  | Metodo | URL | Descricao |
  |--------|-----|-----------|
  | GET | `/admin/` | Painel administrativo do Django |

  ---

  ## Exemplos de uso

  ### Criar usuario

  ```bash
  curl -X POST http://localhost:8000/api/auth/register/ \
    -H "Content-Type: application/json" \
    -d '{
      "user_nickname": "pedro",
      "user_name": "Pedro Fernandes",
      "user_email": "pedro@email.com",
      "user_age": 20,
      "password": "minhasenha123"
    }'
  ```

  ### Login

  ```bash
  curl -X POST http://localhost:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{
      "user_nickname": "pedro",
      "password": "minhasenha123"
    }'
  ```

  ### Listar usuarios

  ```bash
  curl http://localhost:8000/api/users/
  ```

  ### Buscar usuario por nickname

  ```bash
  curl http://localhost:8000/api/users/pedro/
  ```

  ### Atualizar usuario

  ```bash
  curl -X PUT http://localhost:8000/api/users/pedro/ \
    -H "Content-Type: application/json" \
    -d '{
      "user_nickname": "pedro",
      "user_name": "Pedro F. Silva",
      "user_email": "pedro.novo@email.com",
      "user_age": 21,
      "password": "novasenha456"
    }'
  ```

  ### Criar evento

  ```bash
  curl -X POST http://localhost:8000/api/events/ \
    -H "Content-Type: application/json" \
    -d '{
      "title": "Workshop Django",
      "description": "Aula pratica de Django REST Framework",
      "date": "2026-05-15T14:00:00Z",
      "location": "Auditorio FESP",
      "address": "Rua Exemplo, 123",
      "max_participants": 50
    }'
  ```

  ### Listar eventos

  ```bash
  curl http://localhost:8000/api/events/
  ```

  ### Atualizar evento

  ```bash
  curl -X PATCH http://localhost:8000/api/events/1/ \
    -H "Content-Type: application/json" \
    -d '{
      "max_participants": 100
    }'
  ```

  ### Deletar evento

  ```bash
  curl -X DELETE http://localhost:8000/api/events/1/
  ```

  > **Dica:** Acesse `http://localhost:8000/api/events/` no navegador. O DRF mostra uma interface visual onde voce pode testar GET e POST direto na tela.

  ---

  ## Variaveis de ambiente

  Configure no arquivo `.env` na raiz do projeto:

  | Variavel | Descricao | Padrao |
  |----------|-----------|--------|
  | `SECRET_KEY` | Chave secreta do Django | django-insecure-dev-key |
  | `DEBUG` | Modo debug (True/False) | True |
  | `ALLOWED_HOSTS` | Hosts permitidos (separados por virgula) | localhost,127.0.0.1 |
  | `DB_ENGINE` | Engine do banco de dados | django.db.backends.postgresql |
  | `DB_NAME` | Nome do banco | api_topicos_db |
  | `DB_USER` | Usuario do banco | postgres |
  | `DB_PASSWORD` | Senha do banco | postgres123 |
  | `DB_HOST` | Host do banco (nome do servico no Docker) | db |
  | `DB_PORT` | Porta do banco | 5432 |

  ---

  ## Como a dockerizacao funciona

  ### Arquitetura dos containers

  ```
  +-------------------+          +-------------------+
  |   Container web   |          |   Container db    |
  |                   |          |                   |
  |   Python 3.12     | -------> |   PostgreSQL 16   |
  |   Django 6.0.3    |  rede    |   (Alpine)        |
  |   DRF 3.16.1      | interna  |                   |
  |   Porta 8000      |          |   Porta 5432      |
  +-------------------+          +-------------------+
          |                              |
          |                              |
      localhost:8000              Volume: postgres_data
      (acesso externo)            (dados persistentes)
  ```

  ### Fluxo de inicializacao

  ```
  docker-compose up --build
          |
          v
  [Docker constroi a imagem do web]
    - Baixa Python 3.12-slim
    - Instala gcc e libpq-dev
    - Instala dependencias Python (pip install)
    - Copia o codigo do projeto
          |
          v
  [Docker inicia o container db (PostgreSQL)]
    - Cria o banco "api_topicos_db"
    - Cria o usuario "postgres"
    - Healthcheck verifica se esta pronto
          |
          v
  [Docker inicia o container web (Django)]
    - entrypoint.sh roda:
      1. python manage.py migrate (cria as tabelas)
      2. python manage.py collectstatic (arquivos estaticos)
    - Django inicia em 0.0.0.0:8000
          |
          v
  [API disponivel em http://localhost:8000/api/]
  ```

  ### O que cada arquivo faz

  **Dockerfile**
  Define como a imagem do Django e construida. Comeca com Python 3.12-slim, instala as dependencias do sistema (gcc, libpq-dev para compilar o psycopg2), instala as dependencias Python e copia o codigo. Usa multi-stage para que o requirements.txt seja copiado antes do codigo, aproveitando o cache do Docker.

  **docker-compose.yml**
  Orquestra os dois containers. O servico `db` usa a imagem oficial do PostgreSQL 16 Alpine com um volume para persistir dados. O servico `web` constroi a partir do Dockerfile e depende do `db` (sai quando o banco estiver pronto via healthcheck). Os dois se comunicam pela rede interna `app_network`, onde o Django acessa o PostgreSQL pelo hostname `db`.

  **entrypoint.sh**
  Roda toda vez que o container do Django inicia. Aplica as migracoes do banco (`migrate`), coleta arquivos estaticos e entao executa o comando principal (`runserver`). O `set -e` garante que o script pare se qualquer comando falhar.

  **.env**
  Contem as variaveis de ambiente lidas pelo Django (`os.environ.get()`) e pelo docker-compose (`${DB_NAME}`, etc.). O arquivo `.env` nunca deve ser commitado no Git (esta no `.gitignore`).

  **requirements.txt**
  Lista todas as dependencias Python. Inclui `psycopg2-binary` (driver do PostgreSQL) e `gunicorn` (servidor de produo). O `requirements.txt` e copiado e instalado no Dockerfile.

  ---

  ## Estrutura do projeto

  ```
  projetotopicosavancados/
    Dockerfile               # Definicao da imagem Django
    docker-compose.yml       # Orquestracao dos containers
    entrypoint.sh            # Script de inicializacao
    .env                     # Variaveis de ambiente
    .gitignore               # Arquivos ignorados pelo Git
    manage.py                # Entry point do Django
    requirements.txt         # Dependencias Python
    README.md                # Este arquivo

    api_topicos/             # Configuracao do projeto Django
      settings.py            # Configuracoes (DB, apps, middleware)
      urls.py                # Rotas raiz
      wsgi.py / asgi.py      # Entradas WSGI/ASGI

    api_rest/                # Aplicacao principal
      models.py              # Modelos User e Event
      views.py               # Views da API
      serializers.py         # Serializers (conversao JSON)
      urls.py                # Rotas da aplicacao
      admin.py               # Registro no admin
      tests.py               # Testes unitarios
      migrations/            # Migraes do banco
  ```

  ---

  ## Troubleshooting

  ### Erro: "connection refused" ao iniciar

  O Django tentou conectar no PostgreSQL antes dele estar pronto. Solucao:

  ```bash
  docker-compose down
  docker-compose up --build
  ```

  O healthcheck no docker-compose.yml ja previne isso, mas se acontecer, reiniciar resolve.

  ### Erro: porta 8000 em uso

  Outro processo esta usando a porta 8000. Solucao:

  ```bash
  # Descobrir qual processo
  netstat -ano | findstr :8000

  # Matar o processo (substitua PID pelo numero encontrado)
  taskkill /PID <PID> /F
  ```

  Ou altere a porta no docker-compose.yml: `8001:8000` e acesse `localhost:8001`.

  ### Erro: porta 5432 em uso

  Voce tem PostgreSQL rodando localmente. Pare o servico local ou altere a porta no docker-compose.yml: `5433:5432`.

  ### Mudancas no banco nao persistem

  Se rodou `docker-compose down -v`, o volume foi apagado. Use apenas `docker-compose down` para manter os dados.

  ### Preciso recriar o banco do zero

  ```bash
  docker-compose down -v
  docker-compose up --build
  ```

  ### Container nao inicia / erro no build

  ```bash
  # Limpa o cache do Docker e reconstrói
  docker-compose down
  docker system prune -a
  docker-compose up --build
  ```

  ### Ver logs do container

  ```bash
  docker-compose logs -f web    # Logs do Django
  docker-compose logs -f db     # Logs do PostgreSQL
  ```

  ### Acessar o shell do container

  ```bash
  docker-compose exec web bash          # Shell do container Django
  docker-compose exec db psql -U postgres -d api_topicos_db  # Shell do PostgreSQL
  ```
=======
# projetotopicosavancados

API REST para gerenciamento de usurios e eventos, construda com Django 6.0.3 e Django REST Framework 3.16.1.

---

## ndice

1. [Requisitos](#requisitos)
2. [Como rodar com Docker](#como-rodar-com-docker)
3. [Como rodar sem Docker](#como-rodar-sem-docker)
4. [Endpoints da API](#endpoints-da-api)
5. [Exemplos de uso](#exemplos-de-uso)
6. [Variaveis de ambiente](#variaveis-de-ambiente)
7. [Como a dockerizacao funciona](#como-a-dockerizacao-funciona)
8. [Estrutura do projeto](#estrutura-do-projeto)
9. [Troubleshooting](#troubleshooting)

---

## Requisitos

| Obrigatorio | Opcional |
|-------------|----------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Postman ou Insomnia (para testar a API) |
| Git | |

Aps instalar o Docker Desktop, certifique-se que ele esta rodando (icone na bandeja do sistema).

---

## Como rodar com Docker

### Primeira vez

```bash
# 1. Clone o repositorio
git clone https://github.com/augustoluizdev/projetotopicosavancados.git
cd projetotopicosavancados

# 2. Inicie tudo (constroi a imagem e sobe os containers)
docker-compose up --build
```

A API fica disponvel em **http://localhost:8000/api/**

### Comandos uteis

| Comando | O que faz |
|---------|-----------|
| `docker-compose up --build` | Constroi e inicia (mostra logs no terminal) |
| `docker-compose up --build -d` | Constroi e inicia em segundo plano |
| `docker-compose down` | Para os containers |
| `docker-compose down -v` | Para os containers e apaga o banco de dados |
| `docker-compose logs -f` | Mostra os logs em tempo real |
| `docker-compose logs -f web` | Mostra so os logs do Django |
| `docker-compose exec web python manage.py test` | Roda os testes |
| `docker-compose exec web python manage.py createsuperuser` | Cria usuario admin |
| `docker-compose exec web python manage.py shell` | Abre shell Python do Django |
| `docker-compose restart` | Reinicia os containers |

---

## Como rodar sem Docker

Requer Python 3.10+ e PostgreSQL instalados localmente.

```bash
# 1. Ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
source venv/bin/activate      # Linux/macOS

# 2. Dependencias
pip install -r requirements.txt

# 3. Configure o .env para apontar para seu PostgreSQL local
#    ou altere settings.py para usar SQLite

# 4. Migre e rode
python manage.py migrate
python manage.py runserver
```

Para usar SQLite em vez de PostgreSQL (desenvolvimento local), altere em `api_topicos/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

---

## Endpoints da API

### Usurios

| Metodo | URL | Descricao | Body |
|--------|-----|-----------|------|
| GET | `/api/` | Lista todos os usuarios | - |
| POST | `/api/auth/register/` | Cria novo usuario | ver abaixo |
| POST | `/api/auth/login/` | Realiza login | ver abaixo |
| GET | `/api/user/<nick>` | Busca usuario por nickname | - |
| PUT | `/api/user/<nick>` | Atualiza usuario | ver abaixo |

### Eventos

| Metodo | URL | Descricao | Body |
|--------|-----|-----------|------|
| GET | `/api/events/` | Lista todos os eventos | - |
| POST | `/api/events/` | Cria novo evento | ver abaixo |
| GET | `/api/events/<id>/` | Busca evento por ID | - |
| PUT | `/api/events/<id>/` | Atualiza evento completo | ver abaixo |
| PATCH | `/api/events/<id>/` | Atualiza evento parcialmente | qualquer campo |
| DELETE | `/api/events/<id>/` | Deleta evento | - |

### Admin

| Metodo | URL | Descricao |
|--------|-----|-----------|
| GET | `/admin/` | Painel administrativo do Django |

---

## Exemplos de uso

### Criar usuario

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_nickname": "pedro",
    "user_name": "Pedro Fernandes",
    "user_email": "pedro@email.com",
    "user_age": 20,
    "password": "minhasenha123"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_nickname": "pedro",
    "password": "minhasenha123"
  }'
```

### Listar usuarios

```bash
curl http://localhost:8000/api/
```

### Buscar usuario por nickname

```bash
curl http://localhost:8000/api/user/pedro
```

### Atualizar usuario

```bash
curl -X PUT http://localhost:8000/api/user/pedro \
  -H "Content-Type: application/json" \
  -d '{
    "user_nickname": "pedro",
    "user_name": "Pedro F. Silva",
    "user_email": "pedro.novo@email.com",
    "user_age": 21,
    "password": "novasenha456"
  }'
```

### Criar evento

```bash
curl -X POST http://localhost:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Workshop Django",
    "description": "Aula pratica de Django REST Framework",
    "date": "2026-05-15T14:00:00Z",
    "location": "Auditorio FESP",
    "address": "Rua Exemplo, 123",
    "max_participants": 50
  }'
```

### Listar eventos

```bash
curl http://localhost:8000/api/events/
```

### Atualizar evento

```bash
curl -X PATCH http://localhost:8000/api/events/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "max_participants": 100
  }'
```

### Deletar evento

```bash
curl -X DELETE http://localhost:8000/api/events/1/
```

> **Dica:** Acesse `http://localhost:8000/api/events/` no navegador. O DRF mostra uma interface visual onde voce pode testar GET e POST direto na tela.

---

## Variaveis de ambiente

Configure no arquivo `.env` na raiz do projeto:

| Variavel | Descricao | Padrao |
|----------|-----------|--------|
| `SECRET_KEY` | Chave secreta do Django | django-insecure-dev-key |
| `DEBUG` | Modo debug (True/False) | True |
| `ALLOWED_HOSTS` | Hosts permitidos (separados por virgula) | localhost,127.0.0.1 |
| `DB_ENGINE` | Engine do banco de dados | django.db.backends.postgresql |
| `DB_NAME` | Nome do banco | api_topicos_db |
| `DB_USER` | Usuario do banco | postgres |
| `DB_PASSWORD` | Senha do banco | postgres123 |
| `DB_HOST` | Host do banco (nome do servico no Docker) | db |
| `DB_PORT` | Porta do banco | 5432 |

---

## Como a dockerizacao funciona

### Arquitetura dos containers

```
+-------------------+          +-------------------+
|   Container web   |          |   Container db    |
|                   |          |                   |
|   Python 3.12     | -------> |   PostgreSQL 16   |
|   Django 6.0.3    |  rede    |   (Alpine)        |
|   DRF 3.16.1      | interna  |                   |
|   Porta 8000      |          |   Porta 5432      |
+-------------------+          +-------------------+
         |                              |
         |                              |
    localhost:8000              Volume: postgres_data
    (acesso externo)            (dados persistentes)
```

### Fluxo de inicializacao

```
docker-compose up --build
        |
        v
[Docker constroi a imagem do web]
  - Baixa Python 3.12-slim
  - Instala gcc e libpq-dev
  - Instala dependencias Python (pip install)
  - Copia o codigo do projeto
        |
        v
[Docker inicia o container db (PostgreSQL)]
  - Cria o banco "api_topicos_db"
  - Cria o usuario "postgres"
  - Healthcheck verifica se esta pronto
        |
        v
[Docker inicia o container web (Django)]
  - entrypoint.sh roda:
    1. python manage.py migrate (cria as tabelas)
    2. python manage.py collectstatic (arquivos estaticos)
  - Django inicia em 0.0.0.0:8000
        |
        v
[API disponivel em http://localhost:8000/api/]
```

### O que cada arquivo faz

**Dockerfile**
Define como a imagem do Django e construida. Comeca com Python 3.12-slim, instala as dependencias do sistema (gcc, libpq-dev para compilar o psycopg2), instala as dependencias Python e copia o codigo. Usa multi-stage para que o requirements.txt seja copiado antes do codigo, aproveitando o cache do Docker.

**docker-compose.yml**
Orquestra os dois containers. O servico `db` usa a imagem oficial do PostgreSQL 16 Alpine com um volume para persistir dados. O servico `web` constroi a partir do Dockerfile e depende do `db` (sai quando o banco estiver pronto via healthcheck). Os dois se comunicam pela rede interna `app_network`, onde o Django acessa o PostgreSQL pelo hostname `db`.

**entrypoint.sh**
Roda toda vez que o container do Django inicia. Aplica as migracoes do banco (`migrate`), coleta arquivos estaticos e entao executa o comando principal (`runserver`). O `set -e` garante que o script pare se qualquer comando falhar.

**.env**
Contem as variaveis de ambiente lidas pelo Django (`os.environ.get()`) e pelo docker-compose (`${DB_NAME}`, etc.). O arquivo `.env` nunca deve ser commitado no Git (esta no `.gitignore`).

**requirements.txt**
Lista todas as dependencias Python. Inclui `psycopg2-binary` (driver do PostgreSQL) e `gunicorn` (servidor de produo). O `requirements.txt` e copiado e instalado no Dockerfile.

---

## Estrutura do projeto

```
projetotopicosavancados/
  Dockerfile               # Definicao da imagem Django
  docker-compose.yml       # Orquestracao dos containers
  entrypoint.sh            # Script de inicializacao
  .env                     # Variaveis de ambiente
  .gitignore               # Arquivos ignorados pelo Git
  manage.py                # Entry point do Django
  requirements.txt         # Dependencias Python
  README.md                # Este arquivo

  api_topicos/             # Configuracao do projeto Django
    settings.py            # Configuracoes (DB, apps, middleware)
    urls.py                # Rotas raiz
    wsgi.py / asgi.py      # Entradas WSGI/ASGI

  api_rest/                # Aplicacao principal
    models.py              # Modelos User e Event
    views.py               # Views da API
    serializers.py         # Serializers (conversao JSON)
    urls.py                # Rotas da aplicacao
    admin.py               # Registro no admin
    tests.py               # Testes unitarios
    migrations/            # Migraes do banco
```

---

## Troubleshooting

### Erro: "connection refused" ao iniciar

O Django tentou conectar no PostgreSQL antes dele estar pronto. Solucao:

```bash
docker-compose down
      docker-compose up --build
```

O healthcheck no docker-compose.yml ja previne isso, mas se acontecer, reiniciar resolve.

### Erro: porta 8000 em uso

Outro processo esta usando a porta 8000. Solucao:

```bash
# Descobrir qual processo
netstat -ano | findstr :8000

# Matar o processo (substitua PID pelo numero encontrado)
taskkill /PID <PID> /F
```

Ou altere a porta no docker-compose.yml: `8001:8000` e acesse `localhost:8001`.

### Erro: porta 5432 em uso

Voce tem PostgreSQL rodando localmente. Pare o servico local ou altere a porta no docker-compose.yml: `5433:5432`.

### Mudancas no banco nao persistem

Se rodou `docker-compose down -v`, o volume foi apagado. Use apenas `docker-compose down` para manter os dados.

### Preciso recriar o banco do zero

```bash
docker-compose down -v
docker-compose up --build
```

### Container nao inicia / erro no build

```bash
# Limpa o cache do Docker e reconstrói
docker-compose down
docker system prune -a
docker-compose up --build
```

### Ver logs do container

```bash
docker-compose logs -f web    # Logs do Django
docker-compose logs -f db     # Logs do PostgreSQL
```

### Acessar o shell do container

```bash
docker-compose exec web bash          # Shell do container Django
docker-compose exec db psql -U postgres -d api_topicos_db  # Shell do PostgreSQL
```
>>>>>>> origin/main
