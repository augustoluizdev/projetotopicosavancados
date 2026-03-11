"""
JSON Presenters for API responses.
Concrete implementations of presenter interfaces for JSON output.
"""
from typing import List

from src.application.dto.event_dto import EventOutputDTO, EventSummaryDTO
from src.application.ports.presenters import EventPresenter


class JSONEventPresenter(EventPresenter):
    """JSON presenter for event responses."""

    def present_event(self, event_dto: EventOutputDTO) -> dict:
        """Present a single event as JSON."""
        return {
            'success': True,
            'data': {
                'id': event_dto.id,
                'title': event_dto.title,
                'description': event_dto.description,
                'date': event_dto.date,
                'location': event_dto.location,
                'max_participants': event_dto.max_participants,
                'status': event_dto.status,
                'created_at': event_dto.created_at,
                'updated_at': event_dto.updated_at,
            }
        }

class JSONParticipantPresenter:
    """JSON presenter for participant responses."""

    def present_participant(self, participant_dto) -> dict:
        """Present a participant as JSON."""
        return {
            'success': True,
            'data': {
                'id': participant_dto.id,
                'name': participant_dto.name,
                'email': participant_dto.email,
                'created_at': participant_dto.created_at,
                'updated_at': participant_dto.updated_at,
            }
        }
    
    def present_events(self, event_dtos: List[EventSummaryDTO]) -> dict:
        """Present a list of events as JSON."""
        return {
            'success': True,
            'data': [
                {
                    'id': dto.id,
                    'title': dto.title,
                    'date': dto.date,
                    'location': dto.location,
                    'status': dto.status,
                }
                for dto in event_dtos
            ],
            'count': len(event_dtos)
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