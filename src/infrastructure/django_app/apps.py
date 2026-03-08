"""
Django App Configuration for Event Management System.
"""
from django.apps import AppConfig


class EventManagementConfig(AppConfig):
    """Configuration for the event management Django app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.infrastructure.django_app'
    verbose_name = 'Event Management System'

    def ready(self):
        """Initialize the app when Django starts."""
        # Import signals or perform initialization here if needed
        pass