"""
DRF Serializers for API input validation.
"""
from rest_framework import serializers


class CreateEventSerializer(serializers.Serializer):
    """Serializer for creating events."""
    title = serializers.CharField(max_length=200, required=True)
    description = serializers.CharField(required=True)
    date = serializers.DateTimeField(required=True)
    location = serializers.CharField(max_length=300, required=True)
    max_participants = serializers.IntegerField(min_value=1, required=True)


class RegisterParticipantSerializer(serializers.Serializer):
    """Serializer for registering participants."""
    event_id = serializers.CharField(required=True)
    name = serializers.CharField(max_length=200, required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)