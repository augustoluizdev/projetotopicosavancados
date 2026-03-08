"""
Django REST Framework Views for Event Management API.
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from src.application.dto.event_dto import CreateEventInputDTO
from src.infrastructure.config.dependency_container import container


@api_view(['POST'])
def create_event(request):
    """Create a new event."""
    try:
        data = request.data

        # Validate required fields
        required_fields = ['title', 'description', 'date', 'location', 'max_participants']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Create input DTO
        input_dto = CreateEventInputDTO(
            title=data['title'],
            description=data['description'],
            date=data['date'],
            location=data['location'],
            max_participants=int(data['max_participants'])
        )

        # Execute use case
        use_case = container.create_event_use_cases()['create_event']
        result = use_case.execute(input_dto)

        if result.get('success'):
            return Response(result['data'], status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return Response(
            {'error': f'Unexpected error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def list_events(request):
    """List all events or filter by status."""
    try:
        status_filter = request.query_params.get('status')

        # Execute use case
        use_case = container.create_event_use_cases()['list_events']
        result = use_case.execute(status_filter)

        if result.get('success'):
            return Response(result)
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return Response(
            {'error': f'Unexpected error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_event(request, event_id):
    """Get a specific event by ID."""
    try:
        # Get event repository
        repository = container.event_repository
        event = repository.find_by_id(event_id)

        if not event:
            return Response(
                {'error': 'Event not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Convert to DTO
        from src.application.dto.event_dto import EventOutputDTO
        event_dto = EventOutputDTO(
            id=event.id,
            title=event.title,
            description=event.description,
            date=event.date.isoformat(),
            location=event.location,
            max_participants=event.max_participants,
            status=event.status.value,
            created_at=event.created_at.isoformat(),
            updated_at=event.updated_at.isoformat()
        )

        # Present result
        presenter = container.event_presenter
        result = presenter.present_event(event_dto)

        return Response(result)

    except Exception as e:
        return Response(
            {'error': f'Unexpected error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )