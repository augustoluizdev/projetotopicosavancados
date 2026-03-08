"""
Application Ports: Repository Interfaces
Abstract contracts for data access operations.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.event import Event
from src.domain.entities.participant import Participant


class EventRepository(ABC):
    """Abstract interface for event data operations."""

    @abstractmethod
    def save(self, event: Event) -> None:
        """Save an event to the data store."""
        pass

    @abstractmethod
    def find_by_id(self, event_id: str) -> Optional[Event]:
        """Find an event by its ID."""
        pass

    @abstractmethod
    def find_all(self) -> List[Event]:
        """Find all events."""
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Event]:
        """Find events by status."""
        pass

    @abstractmethod
    def delete(self, event_id: str) -> bool:
        """Delete an event by its ID. Returns True if deleted."""
        pass

    @abstractmethod
    def exists(self, event_id: str) -> bool:
        """Check if an event exists."""
        pass


class ParticipantRepository(ABC):
    """Abstract interface for participant data operations."""

    @abstractmethod
    def save(self, participant: Participant) -> None:
        """Save a participant to the data store."""
        pass

    @abstractmethod
    def find_by_id(self, participant_id: str) -> Optional[Participant]:
        """Find a participant by its ID."""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Participant]:
        """Find a participant by email."""
        pass

    @abstractmethod
    def find_by_event(self, event_id: str) -> List[Participant]:
        """Find all participants for an event."""
        pass

    @abstractmethod
    def delete(self, participant_id: str) -> bool:
        """Delete a participant by its ID. Returns True if deleted."""
        pass

    @abstractmethod
    def exists(self, participant_id: str) -> bool:
        """Check if a participant exists."""
        pass