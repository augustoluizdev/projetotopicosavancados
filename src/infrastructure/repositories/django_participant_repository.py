"""
Django Participant Repository Implementation
"""
from typing import List, Optional

from src.application.ports.repositories import ParticipantRepository
from src.domain.entities.participant import Participant

from .models.models import ParticipantModel, EventParticipantModel


class DjangoParticipantRepository(ParticipantRepository):
    """Django ORM implementation of ParticipantRepository."""

    def save(self, participant: Participant) -> None:
        """Save a participant to the database."""
        participant_model, created = ParticipantModel.objects.get_or_create(
            id=participant.id,
            defaults={
                'name': participant.name,
                'email': participant.email,
                'phone': participant.phone,
                'created_at': participant.created_at,
                'updated_at': participant.updated_at,
            }
        )

        if not created:
            # Update existing participant
            participant_model.name = participant.name
            participant_model.email = participant.email
            participant_model.phone = participant.phone
            participant_model.updated_at = participant.updated_at
            participant_model.save()

    def find_by_id(self, participant_id: str) -> Optional[Participant]:
        """Find a participant by its ID."""
        try:
            participant_model = ParticipantModel.objects.get(id=participant_id)
            return self._model_to_entity(participant_model)
        except ParticipantModel.DoesNotExist:
            return None

    def find_by_email(self, email: str) -> Optional[Participant]:
        """Find a participant by email."""
        try:
            participant_model = ParticipantModel.objects.get(email=email)
            return self._model_to_entity(participant_model)
        except ParticipantModel.DoesNotExist:
            return None

    def find_by_event(self, event_id: str) -> List[Participant]:
        """Find all participants for an event."""
        event_participants = EventParticipantModel.objects.filter(
            event_id=event_id
        ).select_related('participant')

        return [
            self._model_to_entity(ep.participant)
            for ep in event_participants
        ]

    def delete(self, participant_id: str) -> bool:
        """Delete a participant by its ID."""
        try:
            participant_model = ParticipantModel.objects.get(id=participant_id)
            participant_model.delete()
            return True
        except ParticipantModel.DoesNotExist:
            return False

    def exists(self, participant_id: str) -> bool:
        """Check if a participant exists."""
        return ParticipantModel.objects.filter(id=participant_id).exists()

    def _model_to_entity(self, model: ParticipantModel) -> Participant:
        """Convert Django model to domain entity."""
        return Participant(
            id=model.id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )