"""
Dependency Injection Container
Manages the creation and injection of dependencies.
"""
from src.application.ports.presenters import EventPresenter, ParticipantPresenter
from src.application.ports.repositories import EventRepository, ParticipantRepository
from src.application.use_cases.create_event_use_case import CreateEventUseCase
from src.application.use_cases.list_events_use_case import ListEventsUseCase
from src.application.use_cases.register_participant_use_case import RegisterParticipantUseCase
from src.infrastructure.repositories.factories import RepositoryFactory
from src.presentation.api.presenters import JSONEventPresenter, JSONParticipantPresenter


class DependencyContainer:
    """Container for managing application dependencies."""

    def __init__(self):
        self._event_repository = None
        self._participant_repository = None
        self._event_presenter = None
        self._participant_presenter = None

    @property
    def event_repository(self) -> EventRepository:
        """Get or create EventRepository instance."""
        if self._event_repository is None:
            self._event_repository = RepositoryFactory.create_event_repository()
        return self._event_repository

    @property
    def participant_repository(self) -> ParticipantRepository:
        """Get or create ParticipantRepository instance."""
        if self._participant_repository is None:
            self._participant_repository = RepositoryFactory.create_participant_repository()
        return self._participant_repository

    @property
    def event_presenter(self) -> EventPresenter:
        """Get or create EventPresenter instance."""
        if self._event_presenter is None:
            self._event_presenter = JSONEventPresenter()
        return self._event_presenter

    @property
    def participant_presenter(self) -> ParticipantPresenter:
        """Get or create ParticipantPresenter instance."""
        if self._participant_presenter is None:
            self._participant_presenter = JSONParticipantPresenter()
        return self._participant_presenter

    def create_event_use_cases(self):
        """Create event-related use cases."""
        return {
            'create_event': CreateEventUseCase(
                self.event_repository,
                self.event_presenter
            ),
            'list_events': ListEventsUseCase(
                self.event_repository,
                self.event_presenter
            ),
        }

    def create_participant_use_cases(self):
        """Create participant-related use cases."""
        return {
            'register_participant': RegisterParticipantUseCase(
                self.event_repository,
                self.participant_repository,
                self.participant_presenter
            ),
        }


# Global container instance
container = DependencyContainer()