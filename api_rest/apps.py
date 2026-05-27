from django.apps import AppConfig


class ApiRestConfig(AppConfig):
    name = 'api_rest'

    def ready(self):
        from . import health_checks  # noqa: F401
