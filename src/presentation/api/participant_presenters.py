"""
JSON Participant Presenter
"""
from typing import List

from src.application.dto.participant_dto import ParticipantOutputDTO, ParticipantSummaryDTO
from src.application.ports.presenters import ParticipantPresenter


class JSONParticipantPresenter(ParticipantPresenter):
    """JSON presenter for participant responses."""

    def present_participant(self, participant_dto: ParticipantOutputDTO) -> dict:
        """Present a single participant as JSON."""
        return {
            'success': True,
            'data': {
                'id': participant_dto.id,
                'name': participant_dto.name,
                'email': participant_dto.email,
                'phone': participant_dto.phone,
                'created_at': participant_dto.created_at,
                'updated_at': participant_dto.updated_at,
            }
        }

    def present_participants(self, participant_dtos: List[ParticipantSummaryDTO]) -> dict:
        """Present a list of participants as JSON."""
        return {
            'success': True,
            'data': [
                {
                    'id': dto.id,
                    'name': dto.name,
                    'email': dto.email,
                }
                for dto in participant_dtos
            ],
            'count': len(participant_dtos)
        }

    def present_success(self, message: str) -> dict:
        """Present a success response."""
        return {
            'success': True,
            'message': message
        }

    def present_error(self, error: str) -> dict:
        """Present an error response."""
        return {
            'success': False,
            'error': error
        }