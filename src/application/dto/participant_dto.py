"""
Data Transfer Objects for Participant operations.
Used for communication between layers.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class RegisterParticipantInputDTO:
    """Input DTO for registering a participant."""
    event_id: str
    name: str
    email: str
    phone: Optional[str] = None


@dataclass
class UpdateParticipantInputDTO:
    """Input DTO for updating participant information."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class ParticipantOutputDTO:
    """Output DTO for participant data."""
    id: str
    name: str
    email: str
    phone: Optional[str]
    created_at: str  # ISO format string
    updated_at: str  # ISO format string


@dataclass
class ParticipantSummaryDTO:
    """Simplified DTO for participant listings."""
    id: str
    name: str
    email: str