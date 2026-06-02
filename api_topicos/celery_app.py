import os
from celery import Celery

# Define a variavel de ambiente padrao do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_topicos.settings')

app = Celery('api_topicos')

# Carrega configuracoes do Django settings com prefixo CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descobre tasks em apps instalados
app.autodiscover_tasks()
