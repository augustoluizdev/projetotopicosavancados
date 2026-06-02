from celery import shared_task
from .models import Event


@shared_task(bind=True, max_retries=3)
def update_event_read_model(self, event_id):
    """Task assincrona que atualiza o Read Model de Eventos
    Executada apos criacao/atualizacao de um evento (Projetor Async)
    """
    try:
        event = Event.objects.get(id=event_id)

        # Calcula ingressos vendidos e disponiveis
        from django.db.models import Sum
        sold_tickets = event.order_items.filter(
            order__status='requested'
        ).aggregate(
            total=Sum('quantity')
        ).get('total') or 0

        available_tickets = event.max_participants - sold_tickets

        event_data = {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'date': event.date,
            'location': event.location,
            'address': event.address,
            'max_participants': event.max_participants,
            'sold_tickets': sold_tickets,
            'available_tickets': available_tickets
        }

        from .read_models import EventReadModel
        EventReadModel.insert_or_update(event_data)

        return f"Read model updated for event {event_id}"

    except Event.DoesNotExist:
        return f"Event {event_id} not found"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
