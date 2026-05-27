import pika
from django.conf import settings
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException
from health_check.plugins import plugin_dir


class RabbitMQHealthCheck(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self):
        if not settings.RABBITMQ_HEALTH_CHECK_ENABLED:
            return

        rabbitmq = settings.RABBITMQ
        credentials = pika.PlainCredentials(rabbitmq['USER'], rabbitmq['PASSWORD'])
        parameters = pika.ConnectionParameters(
            host=rabbitmq['HOST'],
            port=rabbitmq['PORT'],
            credentials=credentials,
            blocked_connection_timeout=3,
            socket_timeout=3,
        )

        try:
            connection = pika.BlockingConnection(parameters)
            connection.close()
        except Exception as exc:
            raise HealthCheckException(f'RabbitMQ indisponivel: {exc}') from exc

    def identifier(self):
        return 'rabbitmq'


plugin_dir.register(RabbitMQHealthCheck)
