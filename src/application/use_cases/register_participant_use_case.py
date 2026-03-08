"""
Use Case: Register Participant
Handles the business logic for registering participants to events.
"""
from src.application.dto.participant_dto import RegisterParticipantInputDTO, ParticipantOutputDTO
from src.application.ports.repositories import EventRepository, ParticipantRepository
from src.application.ports.presenters import ParticipantPresenter
from src.domain.entities.participant import Participant
from src.domain.exceptions.event_not_found import EventNotFound


class RegisterParticipantUseCase:
    """Use case for registering participants to events."""

    def __init__(
        self,
        event_repository: EventRepository,
        participant_repository: ParticipantRepository,
        presenter: ParticipantPresenter
    ):
        self.event_repository = event_repository
        self.participant_repository = participant_repository
        self.presenter = presenter

    def execute(self, input_dto: RegisterParticipantInputDTO) -> dict:
        """Execute the register participant use case."""
        try:
            # Check if event exists
            event = self.event_repository.find_by_id(input_dto.event_id)
            if not event:
                raise EventNotFound(input_dto.event_id)

            # Check if event is published
            if event.status.value != "published":
                return self.presenter.present_error("Cannot register for non-published events")

            # Check if participant already exists with this email
            existing_participant = self.participant_repository.find_by_email(input_dto.email)
            if existing_participant:
                return self.presenter.present_error("Participant with this email already exists")

            # Check event capacity
            current_participants = self.participant_repository.find_by_event(input_dto.event_id)
            if len(current_participants) >= event.max_participants:
                return self.presenter.present_error("Event is at maximum capacity")

            # Create domain entity
            participant = Participant(
                name=input_dto.name,
                email=input_dto.email,
                phone=input_dto.phone
            )

            # Save to repository
            self.participant_repository.save(participant)

            # Create output DTO
            output_dto = ParticipantOutputDTO(
                id=participant.id,
                name=participant.name,
                email=participant.email,
                phone=participant.phone,
                created_at=participant.created_at.isoformat(),
                updated_at=participant.updated_at.isoformat()
            )

            # Present result
            return self.presenter.present_participant(output_dto)

        except EventNotFound as e:
            return self.presenter.present_error(str(e))
        except ValueError as e:
            return self.presenter.present_error(str(e))
        except Exception as e:
            return self.presenter.present_error(f"Unexpected error: {str(e)}")