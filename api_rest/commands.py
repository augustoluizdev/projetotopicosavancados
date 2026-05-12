from django.db import transaction
from .models import Event


class EventCommandService:
    """Servico de Command para operacoes de escrita de Eventos (CQRS - Command Side)"""

    @staticmethod
    def create_event(data):
        """Cria um evento no banco de escrita (PostgreSQL via Django ORM)"""
        with transaction.atomic():
            event = Event.objects.create(
                title=data['title'],
                description=data.get('description', ''),
                date=data['date'],
                location=data['location'],
                address=data.get('address', ''),
                max_participants=data['max_participants']
            )
        return event

    @staticmethod
    def update_event(event_id, data):
        """Atualiza um evento no banco de escrita"""
        with transaction.atomic():
            event = Event.objects.get(id=event_id)
            for key, value in data.items():
                setattr(event, key, value)
            event.save()
        return event

    @staticmethod
    def delete_event(event_id):
        """Remove um evento do banco de escrita"""
        with transaction.atomic():
            event = Event.objects.get(id=event_id)
            event.delete()
        return True
