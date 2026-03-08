"""
Unit Tests for Application Use Cases.
"""
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from src.application.dto.event_dto import CreateEventInputDTO
from src.application.use_cases.create_event_use_case import CreateEventUseCase
from src.domain.entities.event import Event


class TestCreateEventUseCase:
    """Test cases for CreateEventUseCase."""

    def test_create_event_success(self):
        """Test successful event creation."""
        # Arrange
        mock_repository = Mock()
        mock_presenter = Mock()

        future_date = datetime.now() + timedelta(days=1)
        input_dto = CreateEventInputDTO(
            title="Test Event",
            description="A test event",
            date=future_date.isoformat(),
            location="Test Location",
            max_participants=100
        )

        expected_event = Event(
            title="Test Event",
            description="A test event",
            date=future_date,
            location="Test Location",
            max_participants=100
        )

        mock_repository.save = Mock()
        mock_presenter.present_event = Mock(return_value={'success': True, 'data': {}})

        use_case = CreateEventUseCase(mock_repository, mock_presenter)

        # Act
        result = use_case.execute(input_dto)

        # Assert
        assert result['success'] is True
        mock_repository.save.assert_called_once()
        mock_presenter.present_event.assert_called_once()

    def test_create_event_validation_error(self):
        """Test event creation with validation error."""
        # Arrange
        mock_repository = Mock()
        mock_presenter = Mock()

        # Past date should cause validation error
        past_date = datetime.now() - timedelta(days=1)
        input_dto = CreateEventInputDTO(
            title="Test Event",
            description="A test event",
            date=past_date.isoformat(),
            location="Test Location",
            max_participants=100
        )

        mock_presenter.present_error = Mock(return_value={'success': False, 'error': 'Validation error'})

        use_case = CreateEventUseCase(mock_repository, mock_presenter)

        # Act
        result = use_case.execute(input_dto)

        # Assert
        assert result['success'] is False
        assert 'error' in result
        mock_repository.save.assert_not_called()