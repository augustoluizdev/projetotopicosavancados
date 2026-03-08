"""
Participant API Views
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from src.application.dto.participant_dto import RegisterParticipantInputDTO
from src.infrastructure.config.dependency_container import container


@api_view(['POST'])
def register_participant(request):
    """Register a participant for an event."""
    try:
        data = request.data

        # Validate required fields
        required_fields = ['event_id', 'name', 'email']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Create input DTO
        input_dto = RegisterParticipantInputDTO(
            event_id=data['event_id'],
            name=data['name'],
            email=data['email'],
            phone=data.get('phone')
        )

        # Execute use case
        use_case = container.create_participant_use_cases()['register_participant']
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
def list_event_participants(request, event_id):
    """List all participants for a specific event."""
    try:
        # Get participants for event
        repository = container.participant_repository
        participants = repository.find_by_event(event_id)

        # Convert to summary DTOs
        from src.application.dto.participant_dto import ParticipantSummaryDTO
        participant_dtos = [
            ParticipantSummaryDTO(
                id=p.id,
                name=p.name,
                email=p.email
            )
            for p in participants
        ]

        # Present result
        presenter = container.participant_presenter
        result = presenter.present_participants(participant_dtos)

        return Response(result)

    except Exception as e:
        return Response(
            {'error': f'Unexpected error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )