"""
Pytest configuration and fixtures for the project.
"""
import pytest
from datetime import datetime, timedelta


@pytest.fixture
def future_date():
    """Fixture for a future date."""
    return datetime.now() + timedelta(days=7)


@pytest.fixture
def past_date():
    """Fixture for a past date."""
    return datetime.now() - timedelta(days=1)


@pytest.fixture
def sample_event_data(future_date):
    """Fixture for sample event data."""
    return {
        'title': 'Sample Event',
        'description': 'A sample event for testing',
        'date': future_date.isoformat(),
        'location': 'Sample Location',
        'max_participants': 50
    }


@pytest.fixture
def sample_participant_data():
    """Fixture for sample participant data."""
    return {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+1234567890'
    }