"""
URL Configuration for Event Management API.
"""
from django.urls import path

from .event_views import create_event, get_event, list_events
from .participant_views import list_event_participants, register_participant

app_name = 'api'

urlpatterns = [
    # Event endpoints
    path('events/', list_events, name='list_events'),
    path('events/create/', create_event, name='create_event'),
    path('events/<str:event_id>/', get_event, name='get_event'),

    # Participant endpoints
    path('events/<str:event_id>/participants/', list_event_participants, name='list_event_participants'),
    path('participants/register/', register_participant, name='register_participant'),
]