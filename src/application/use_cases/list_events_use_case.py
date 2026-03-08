"""
Use Case: List Events
Handles the business logic for listing events.
"""
from typing import List, Optional

from src.application.dto.event_dto import EventSummaryDTO
from src.application.ports.repositories import EventRepository
from src.application.ports.presenters import EventPresenter
from src.domain.entities.event import Event


class ListEventsUseCase:
    """Use case for listing events."""

    def __init__(
        self,
        event_repository: EventRepository,
        presenter: EventPresenter
    ):
        self.event_repository = event_repository
        self.presenter = presenter

    def execute(self, status_filter: Optional[str] = None) -> dict:
        """Execute the list events use case."""
        try:
            # Get events from repository
            if status_filter:
                events = self.event_repository.find_by_status(status_filter)
            else:
                events = self.event_repository.find_all()

            # Convert to summary DTOs
            event_dtos = [
                EventSummaryDTO(
                    id=event.id,
                    title=event.title,
                    date=event.date.isoformat(),
                    location=event.location,
                    status=event.status.value
                )
                for event in events
            ]

            # Present result
            return self.presenter.present_events(event_dtos)

        except Exception as e:
            return self.presenter.present_error(f"Unexpected error: {str(e)}")