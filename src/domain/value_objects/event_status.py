"""
Value Object for Event Status
Represents the possible states of an event in the system.
"""
from enum import Enum


class EventStatus(Enum):
    """Enumeration of possible event statuses."""
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_string(cls, value: str) -> 'EventStatus':
        """Create EventStatus from string value."""
        for status in cls:
            if status.value == value:
                return status
        raise ValueError(f"Invalid event status: {value}")