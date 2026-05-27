from django.apps import AppConfig


class ApiRestConfig(AppConfig):
    name = 'api_rest'

    def ready(self):
        """Executado quando o Django inicia"""
        pass
