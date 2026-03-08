"""
Django Admin Configuration for Event Management Models.
"""
from django.contrib import admin

from .models.models import EventModel, ParticipantModel, EventParticipantModel


@admin.register(EventModel)
class EventAdmin(admin.ModelAdmin):
    """Admin interface for Event model."""
    list_display = ['title', 'date', 'location', 'status', 'max_participants', 'created_at']
    list_filter = ['status', 'date', 'created_at']
    search_fields = ['title', 'description', 'location']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ParticipantModel)
class ParticipantAdmin(admin.ModelAdmin):
    """Admin interface for Participant model."""
    list_display = ['name', 'email', 'phone', 'created_at']
    search_fields = ['name', 'email']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(EventParticipantModel)
class EventParticipantAdmin(admin.ModelAdmin):
    """Admin interface for Event-Participant relationship."""
    list_display = ['event', 'participant', 'registered_at']
    list_filter = ['registered_at']
    search_fields = ['event__title', 'participant__name', 'participant__email']
    ordering = ['-registered_at']
    readonly_fields = ['id', 'registered_at']