"""
Use Case: Create Event
Handles the business logic for creating new events.
"""
from datetime import datetime

from src.application.dto.event_dto import CreateEventInputDTO, EventOutputDTO
from src.application.ports.repositories import EventRepository
from src.application.ports.presenters import EventPresenter
from src.domain.entities.event import Event
from src.domain.value_objects.event_status import EventStatus


class CreateEventUseCase:
    """Use case for creating events."""

    def __init__(
        self,
        event_repository: EventRepository,
        presenter: EventPresenter
    ):
        self.event_repository = event_repository
        self.presenter = presenter

    def execute(self, input_dto: CreateEventInputDTO) -> dict:
        """Execute the create event use case."""
        try:
            # Parse date from ISO string
            event_date = datetime.fromisoformat(input_dto.date)

            # Create domain entity
            event = Event(
                title=input_dto.title,
                description=input_dto.description,
                date=event_date,
                location=input_dto.location,
                max_participants=input_dto.max_participants
            )

            # Save to repository
            self.event_repository.save(event)

            # Create output DTO
            output_dto = EventOutputDTO(
                id=event.id,
                title=event.title,
                description=event.description,
                date=event.date.isoformat(),
                location=event.location,
                max_participants=event.max_participants,
                status=event.status.value,
                created_at=event.created_at.isoformat(),
                updated_at=event.updated_at.isoformat()
            )

            # Present result
            return self.presenter.present_event(output_dto)

        except ValueError as e:
            return self.presenter.present_error(str(e))
        except Exception as e:
            return self.presenter.present_error(f"Unexpected error: {str(e)}")