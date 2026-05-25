from __future__ import annotations

import logging
import time
import uuid

from .logging_utils import correlation_id_context

request_logger = logging.getLogger('api.request')


class CorrelationIdMiddleware:
    header_name = 'HTTP_X_CORRELATION_ID'
    response_header = 'X-Correlation-ID'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        correlation_id = request.META.get(self.header_name) or str(uuid.uuid4())
        request.correlation_id = correlation_id
        token = correlation_id_context.set(correlation_id)
        started_at = time.perf_counter()

        try:
            response = self.get_response(request)
        except Exception:
            elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
            request_logger.exception(
                'HTTP request failed',
                extra={
                    'method': request.method,
                    'path': request.get_full_path(),
                    'status_code': 500,
                    'duration_ms': elapsed_ms,
                    'remote_addr': request.META.get('REMOTE_ADDR'),
                },
            )
            raise
        else:
            elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
            response[self.response_header] = correlation_id
            request_logger.info(
                'HTTP request completed',
                extra={
                    'method': request.method,
                    'path': request.get_full_path(),
                    'status_code': response.status_code,
                    'duration_ms': elapsed_ms,
                    'remote_addr': request.META.get('REMOTE_ADDR'),
                },
            )
            return response
        finally:
            correlation_id_context.reset(token)
