"""
Domain Entity: Event
Represents an event in the event management system.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from src.domain.value_objects.event_status import EventStatus


@dataclass
class Event:
    """Domain entity representing an event."""
    title: str
    description: str
    date: datetime
    location: str
    max_participants: int
    status: EventStatus = field(default=EventStatus.DRAFT)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate entity invariants after initialization."""
        if not self.title.strip():
            raise ValueError("Event title cannot be empty")
        if self.max_participants <= 0:
            raise ValueError("Max participants must be positive")
        if self.date < datetime.now():
            raise ValueError("Event date cannot be in the past")

    def publish(self) -> None:
        """Publish the event."""
        if self.status != EventStatus.DRAFT:
            raise ValueError("Only draft events can be published")
        self.status = EventStatus.PUBLISHED
        self.updated_at = datetime.now()

    def cancel(self) -> None:
        """Cancel the event."""
        if self.status == EventStatus.COMPLETED:
            raise ValueError("Completed events cannot be cancelled")
        self.status = EventStatus.CANCELLED
        self.updated_at = datetime.now()

    def complete(self) -> None:
        """Mark the event as completed."""
        if self.status != EventStatus.PUBLISHED:
            raise ValueError("Only published events can be completed")
        self.status = EventStatus.COMPLETED
        self.updated_at = datetime.now()

    def update_details(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        date: Optional[datetime] = None,
        location: Optional[str] = None,
        max_participants: Optional[int] = None
    ) -> None:
        """Update event details."""
        if self.status == EventStatus.COMPLETED:
            raise ValueError("Completed events cannot be modified")

        if title is not None:
            if not title.strip():
                raise ValueError("Event title cannot be empty")
            self.title = title

        if description is not None:
            self.description = description

        if date is not None:
            if date < datetime.now():
                raise ValueError("Event date cannot be in the past")
            self.date = date

        if location is not None:
            self.location = location

        if max_participants is not None:
            if max_participants <= 0:
                raise ValueError("Max participants must be positive")
            self.max_participants = max_participants

        self.updated_at = datetime.now()