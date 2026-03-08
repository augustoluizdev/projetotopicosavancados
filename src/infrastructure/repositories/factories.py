"""
Dependency Injection Factories
Provides concrete implementations for dependency injection.
"""
from src.application.ports.repositories import EventRepository, ParticipantRepository
from src.infrastructure.repositories.django_event_repository import DjangoEventRepository
from src.infrastructure.repositories.django_participant_repository import DjangoParticipantRepository


class RepositoryFactory:
    """Factory for creating repository instances."""

    @staticmethod
    def create_event_repository() -> EventRepository:
        """Create an EventRepository instance."""
        return DjangoEventRepository()

    @staticmethod
    def create_participant_repository() -> ParticipantRepository:
        """Create a ParticipantRepository instance."""
        return DjangoParticipantRepository()