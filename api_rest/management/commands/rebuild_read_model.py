from django.core.management.base import BaseCommand
from django.db import connection
from api_rest.models import Event
from django.db.models import Sum


class Command(BaseCommand):
    help = 'Reconstrói a tabela de Read Model de Eventos (CQRS)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Reconstruindo Read Model de Eventos...')

        with connection.cursor() as cursor:
            # Limpa a tabela
            cursor.execute("TRUNCATE TABLE readmodel_event")

            # Popula com dados atuais
            for event in Event.objects.all():
                sold = event.order_items.filter(
                    order__status='requested'
                ).aggregate(
                    total=Sum('quantity')
                ).get('total') or 0

                available = event.max_participants - sold

                cursor.execute("""
                    INSERT INTO readmodel_event
                    (id, title, description, date, location, address, max_participants, sold_tickets, available_tickets, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, [
                    event.id, event.title, event.description, event.date,
                    event.location, event.address, event.max_participants,
                    sold, available
                ])

        self.stdout.write(self.style.SUCCESS('Read Model reconstruído com sucesso!'))
