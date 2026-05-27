# ============================================================
# Dockerfile - Backend Django (projetotopicosavancados)
# ============================================================
#
# Este arquivo define como a imagem do container do Django
# deve ser construida. Cada instrucao representa uma camada
# da imagem, e a ordem importa para o cache do Docker.
#
# Fluxo de construcao:
#   1. Parte da imagem base do Python 3.12
#   2. Instala dependencias do sistema (gcc, libpq-dev)
#   3. Copia o requirements.txt e instala as dependencias Python
#   4. Copia o codigo do projeto para o container
#   5. Libera a porta 8000 e define o entrypoint
# ============================================================

# Imagem base: Python 3.12 com Debian Slim
# - Slim: versao menor, so com o essencial
# - 3.12: versao estavel e compativel com Django 6.0
FROM python:3.12-slim

# PYTHONDONTWRITEBYTECODE=1
#   Impede o Python de criar arquivos .pyc (cache de bytecode)
#   Dentro do container isso so ocupa espaco desnecessario
ENV PYTHONDONTWRITEBYTECODE=1

# PYTHONUNBUFFERED=1
#   Forca o Python a imprimir os logs imediatamente (sem buffer)
#   Sem isso, os logs do Django podem demorar para aparecer
#   no `docker-compose logs`, dificultando o debug
ENV PYTHONUNBUFFERED=1

# Define o diretorio de trabalho dentro do container
# Todos os comandos seguintes serao executados a partir de /app
WORKDIR /app

# Instala dependencias do sistema operacional necessarias
# para compilar pacotes Python que tem extensoes em C:
#   gcc: compilador C, necessario para psycopg2
#   libpq-dev: bibliotecas de desenvolvimento do PostgreSQL
#   --no-install-recommends: nao instala pacotes sugeridos (imagem menor)
#   rm -rf /var/lib/apt/lists/*: limpa cache do apt (imagem menor)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas o requirements.txt primeiro (antes do codigo todo)
# Isso aproveita o cache do Docker: se o requirements.txt nao mudar,
# o Docker nao reinstala as dependencias, so copia o codigo novo
COPY requirements.txt .

# Instala as dependencias Python
# --no-cache-dir: nao guarda cache do pip (imagem menor)
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o codigo do projeto para /app dentro do container
# Isso vem DEPOIS do pip install para aproveitar o cache
COPY . .

# Garante que o entrypoint rode em Linux mesmo quando o projeto foi
# editado/clonado em Windows.
RUN chmod +x /app/entrypoint.sh

# Libera a porta 8000 para comunicacao externa
# Nao publica a porta (isso e feito no docker-compose.yml)
EXPOSE 8000

# Define o entrypoint: script que roda quando o container inicia
# O entrypoint.sh executa migrations e depois o comando principal
# (no caso, `python manage.py runserver 0.0.0.0:8000` do docker-compose)
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
