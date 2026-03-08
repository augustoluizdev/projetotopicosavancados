"""
Domain Entity: Participant
Represents a participant in the event management system.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass
class Participant:
    """Domain entity representing a participant."""
    name: str
    email: str
    phone: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate entity invariants after initialization."""
        if not self.name.strip():
            raise ValueError("Participant name cannot be empty")
        if not self.email.strip():
            raise ValueError("Participant email cannot be empty")
        if "@" not in self.email:
            raise ValueError("Invalid email format")

    def update_contact_info(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> None:
        """Update participant contact information."""
        if name is not None:
            if not name.strip():
                raise ValueError("Participant name cannot be empty")
            self.name = name

        if email is not None:
            if not email.strip():
                raise ValueError("Participant email cannot be empty")
            if "@" not in email:
                raise ValueError("Invalid email format")
            self.email = email

        if phone is not None:
            self.phone = phone

        self.updated_at = datetime.now()