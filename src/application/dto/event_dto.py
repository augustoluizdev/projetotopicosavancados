"""
Data Transfer Objects for Event operations.
Used for communication between layers.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.value_objects.event_status import EventStatus


@dataclass
class CreateEventInputDTO:
    """Input DTO for creating an event."""
    title: str
    description: str
    date: str  # ISO format string
    location: str
    max_participants: int


@dataclass
class UpdateEventInputDTO:
    """Input DTO for updating an event."""
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None  # ISO format string
    location: Optional[str] = None
    max_participants: Optional[int] = None


@dataclass
class EventOutputDTO:
    """Output DTO for event data."""
    id: str
    title: str
    description: str
    date: str  # ISO format string
    location: str
    max_participants: int
    status: str
    created_at: str  # ISO format string
    updated_at: str  # ISO format string


@dataclass
class EventSummaryDTO:
    """Simplified DTO for event listings."""
    id: str
    title: str
    date: str  # ISO format string
    location: str
    status: str