#!/bin/sh
# ============================================================
# entrypoint.sh - Script de inicializacao do container Django
# ============================================================

set -e

if [ "$SKIP_MIGRATIONS" != "True" ]; then
    echo "Aplicando migracoes..."
    python manage.py migrate --noinput

    echo "Coletando arquivos estaticos..."
    python manage.py collectstatic --noinput --clear 2>/dev/null || true
else
    echo "Pulando migracoes neste servico..."
fi

echo "Iniciando servico..."
exec "$@"
