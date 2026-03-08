"""
Unit Tests for Domain Entities.
"""
import pytest
from datetime import datetime, timedelta

from src.domain.entities.event import Event
from src.domain.entities.participant import Participant
from src.domain.value_objects.event_status import EventStatus


class TestEvent:
    """Test cases for Event entity."""

    def test_create_valid_event(self):
        """Test creating a valid event."""
        future_date = datetime.now() + timedelta(days=1)
        event = Event(
            title="Test Event",
            description="A test event",
            date=future_date,
            location="Test Location",
            max_participants=100
        )

        assert event.title == "Test Event"
        assert event.status == EventStatus.DRAFT
        assert event.id is not None

    def test_event_creation_validation(self):
        """Test event creation validation."""
        past_date = datetime.now() - timedelta(days=1)

        with pytest.raises(ValueError, match="Event date cannot be in the past"):
            Event(
                title="Test Event",
                description="A test event",
                date=past_date,
                location="Test Location",
                max_participants=100
            )

        with pytest.raises(ValueError, match="Event title cannot be empty"):
            Event(
                title="",
                description="A test event",
                date=datetime.now() + timedelta(days=1),
                location="Test Location",
                max_participants=100
            )

    def test_event_publish(self):
        """Test publishing an event."""
        future_date = datetime.now() + timedelta(days=1)
        event = Event(
            title="Test Event",
            description="A test event",
            date=future_date,
            location="Test Location",
            max_participants=100
        )

        event.publish()
        assert event.status == EventStatus.PUBLISHED

    def test_event_complete(self):
        """Test completing an event."""
        future_date = datetime.now() + timedelta(days=1)
        event = Event(
            title="Test Event",
            description="A test event",
            date=future_date,
            location="Test Location",
            max_participants=100
        )

        event.publish()
        event.complete()
        assert event.status == EventStatus.COMPLETED


class TestParticipant:
    """Test cases for Participant entity."""

    def test_create_valid_participant(self):
        """Test creating a valid participant."""
        participant = Participant(
            name="John Doe",
            email="john@example.com",
            phone="+1234567890"
        )

        assert participant.name == "John Doe"
        assert participant.email == "john@example.com"
        assert participant.phone == "+1234567890"
        assert participant.id is not None

    def test_participant_creation_validation(self):
        """Test participant creation validation."""
        with pytest.raises(ValueError, match="Participant name cannot be empty"):
            Participant(name="", email="john@example.com")

        with pytest.raises(ValueError, match="Participant email cannot be empty"):
            Participant(name="John Doe", email="")

        with pytest.raises(ValueError, match="Invalid email format"):
            Participant(name="John Doe", email="invalid-email")