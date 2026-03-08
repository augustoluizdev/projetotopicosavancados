"""
Application Ports: Presenter Interfaces
Abstract contracts for output formatting operations.
"""
from abc import ABC, abstractmethod
from typing import List

from src.application.dto.event_dto import EventOutputDTO, EventSummaryDTO
from src.application.dto.participant_dto import ParticipantOutputDTO, ParticipantSummaryDTO


class EventPresenter(ABC):
    """Abstract interface for event presentation operations."""

    @abstractmethod
    def present_event(self, event_dto: EventOutputDTO) -> dict:
        """Present a single event."""
        pass

    @abstractmethod
    def present_events(self, event_dtos: List[EventSummaryDTO]) -> dict:
        """Present a list of events."""
        pass

    @abstractmethod
    def present_success(self, message: str) -> dict:
        """Present a success response."""
        pass

    @abstractmethod
    def present_error(self, error: str) -> dict:
        """Present an error response."""
        pass


class ParticipantPresenter(ABC):
    """Abstract interface for participant presentation operations."""

    @abstractmethod
    def present_participant(self, participant_dto: ParticipantOutputDTO) -> dict:
        """Present a single participant."""
        pass

    @abstractmethod
    def present_participants(self, participant_dtos: List[ParticipantSummaryDTO]) -> dict:
        """Present a list of participants."""
        pass

    @abstractmethod
    def present_success(self, message: str) -> dict:
        """Present a success response."""
        pass

    @abstractmethod
    def present_error(self, error: str) -> dict:
        """Present an error response."""
        pass