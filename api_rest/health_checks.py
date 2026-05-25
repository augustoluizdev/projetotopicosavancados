from __future__ import annotations

import dataclasses
from pathlib import Path
from time import perf_counter

import pika
from django.conf import settings
from django.db import Error as DatabaseError
from django.db import connection
from django.http import JsonResponse
from django.views import View
from health_check.base import HealthCheck
from health_check.exceptions import ServiceUnavailable, ServiceWarning
from health_check.views import HealthCheckView


@dataclasses.dataclass
class DatabaseHealthCheck(HealthCheck):
    name: str = dataclasses.field(default='database', init=False)

    def run(self) -> None:
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                result = cursor.fetchone()
        except DatabaseError as exc:
            raise ServiceUnavailable('database connection failed') from exc

        if result != (1,):
            raise ServiceUnavailable('database health query returned an unexpected result')


@dataclasses.dataclass
class RabbitMQHealthCheck(HealthCheck):
    name: str = dataclasses.field(default='rabbitmq', init=False)

    def run(self) -> None:
        rabbitmq = settings.RABBITMQ
        credentials = pika.PlainCredentials(rabbitmq['USER'], rabbitmq['PASSWORD'])
        parameters = pika.ConnectionParameters(
            host=rabbitmq['HOST'],
            port=rabbitmq['PORT'],
            credentials=credentials,
            socket_timeout=5,
            blocked_connection_timeout=5,
        )

        try:
            connection = pika.BlockingConnection(parameters)
        except Exception as exc:
            raise ServiceUnavailable('rabbitmq connection failed') from exc

        try:
            channel = connection.channel()
            channel.close()
        finally:
            connection.close()


@dataclasses.dataclass
class LogsDirectoryHealthCheck(HealthCheck):
    name: str = dataclasses.field(default='logs-directory', init=False)

    def run(self) -> None:
        logs_dir = Path(settings.LOGS_DIR)
        test_file = logs_dir / '.health-check'
        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
            test_file.write_text('ok', encoding='utf-8')
            test_file.unlink()
        except OSError as exc:
            raise ServiceUnavailable('logs directory is not writable') from exc


class ObservabilityHealthCheckView(HealthCheckView):
    def get_check_name(self, check: HealthCheck) -> str:
        return getattr(check, 'name', check.__class__.__name__.replace('HealthCheck', '').lower())

    def get_status_label(self, result) -> str:
        if result.error is None:
            return 'Healthy'
        if isinstance(result.error, ServiceWarning):
            return 'Degraded'
        return 'Unhealthy'

    def get_overall_status(self) -> str:
        statuses = [self.get_status_label(result) for result in self.results]
        if any(status == 'Unhealthy' for status in statuses):
            return 'Unhealthy'
        if any(status == 'Degraded' for status in statuses):
            return 'Degraded'
        return 'Healthy'

    def render_to_response_json(self, status):
        entries = {}
        for result in self.results:
            name = self.get_check_name(result.check)
            entry = {
                'status': self.get_status_label(result),
                'duration_ms': round(result.time_taken * 1000, 2),
            }
            if result.error is not None:
                entry['description'] = str(result.error)
            entries[name] = entry

        return JsonResponse(
            {
                'status': self.get_overall_status(),
                'entries': entries,
            },
            status=status,
        )


class HealthView(ObservabilityHealthCheckView):
    checks = (
        DatabaseHealthCheck,
        RabbitMQHealthCheck,
        LogsDirectoryHealthCheck,
    )


class ReadinessView(ObservabilityHealthCheckView):
    checks = (
        DatabaseHealthCheck,
        RabbitMQHealthCheck,
    )


class LivenessView(View):
    def get(self, request, *args, **kwargs):
        started_at = perf_counter()
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        return JsonResponse(
            {
                'status': 'Healthy',
                'entries': {},
                'duration_ms': duration_ms,
            }
        )
