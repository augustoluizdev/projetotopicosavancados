"""
Django Repository Implementations
Concrete implementations of repository interfaces using Django ORM.
"""
from typing import List, Optional

from src.application.ports.repositories import EventRepository, ParticipantRepository
from src.domain.entities.event import Event
from src.domain.entities.participant import Participant
from src.domain.value_objects.event_status import EventStatus

from .models.models import EventModel, ParticipantModel, EventParticipantModel


class DjangoEventRepository(EventRepository):
    """Django ORM implementation of EventRepository."""

    def save(self, event: Event) -> None:
        """Save an event to the database."""
        event_model, created = EventModel.objects.get_or_create(
            id=event.id,
            defaults={
                'title': event.title,
                'description': event.description,
                'date': event.date,
                'location': event.location,
                'max_participants': event.max_participants,
                'status': event.status.value,
                'created_at': event.created_at,
                'updated_at': event.updated_at,
            }
        )

        if not created:
            # Update existing event
            event_model.title = event.title
            event_model.description = event.description
            event_model.date = event.date
            event_model.location = event.location
            event_model.max_participants = event.max_participants
            event_model.status = event.status.value
            event_model.updated_at = event.updated_at
            event_model.save()

    def find_by_id(self, event_id: str) -> Optional[Event]:
        """Find an event by its ID."""
        try:
            event_model = EventModel.objects.get(id=event_id)
            return self._model_to_entity(event_model)
        except EventModel.DoesNotExist:
            return None

    def find_all(self) -> List[Event]:
        """Find all events."""
        event_models = EventModel.objects.all()
        return [self._model_to_entity(model) for model in event_models]

    def find_by_status(self, status: str) -> List[Event]:
        """Find events by status."""
        event_models = EventModel.objects.filter(status=status)
        return [self._model_to_entity(model) for model in event_models]

    def delete(self, event_id: str) -> bool:
        """Delete an event by its ID."""
        try:
            event_model = EventModel.objects.get(id=event_id)
            event_model.delete()
            return True
        except EventModel.DoesNotExist:
            return False

    def exists(self, event_id: str) -> bool:
        """Check if an event exists."""
        return EventModel.objects.filter(id=event_id).exists()

    def _model_to_entity(self, model: EventModel) -> Event:
        """Convert Django model to domain entity."""
        return Event(
            id=model.id,
            title=model.title,
            description=model.description,
            date=model.date,
            location=model.location,
            max_participants=model.max_participants,
            status=EventStatus.from_string(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )