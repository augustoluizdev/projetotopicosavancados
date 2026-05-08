#!/bin/bash
# ============================================================
# entrypoint.sh - Script de inicializacao do container Django
# ============================================================
#
# Este script roda TODA VEZ que o container inicia.
# Ele executa tarefas de preparacao antes de subir o servidor.
#
# Fluxo:
#   1. Aplica as migracoes do banco de dados
#   2. Coleta arquivos estaticos (CSS, JS, imagens)
#   3. Inicia o servidor Django (comando passado pelo docker-compose)
#
# O `set -e` faz o script parar imediatamente se qualquer
# comando falhar, evitando que o servidor suba com erros
# ============================================================

# Encerra o script imediatamente se qualquer comando retornar erro
set -e

# Aplica todas as migracoes pendentes do Django
# --noinput: nao pergunta confirmacao (automatiza no Docker)
# Isso cria/atualiza as tabelas no PostgreSQL
echo "Aplicando migracoes..."
python manage.py migrate --noinput

# Coleta arquivos estaticos para a pasta STATIC_ROOT
# --noinput: nao pergunta confirmacao
# --clear: remove arquivos antigos antes de copiar
# 2>/dev/null || true: ignora erros se nao houver arquivos estaticos
echo "Coletando arquivos estaticos..."
python manage.py collectstatic --noinput --clear 2>/dev/null || true

# Executa o comando principal passado pelo docker-compose
# No nosso caso: python manage.py runserver 0.0.0.0:8000
# O `exec` substitui o processo do shell pelo do Python,
# garantindo que sinais (como Ctrl+C) cheguem ao Django corretamente
echo "Iniciando servidor..."
exec "$@"
