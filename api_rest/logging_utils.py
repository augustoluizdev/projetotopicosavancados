from __future__ import annotations

import contextvars
import logging
from pathlib import Path

from pythonjsonlogger import jsonlogger


correlation_id_context: contextvars.ContextVar[str] = contextvars.ContextVar(
    'correlation_id',
    default='',
)


class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_context.get() or '-'
        return True


class StructuredJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        if 'asctime' in log_record:
            log_record['timestamp'] = log_record.pop('asctime')
        if 'levelname' in log_record:
            log_record['level'] = log_record.pop('levelname')
        else:
            log_record.setdefault('level', record.levelname)
        if 'name' in log_record:
            log_record['logger'] = log_record.pop('name')
        else:
            log_record.setdefault('logger', record.name)
        log_record.setdefault('module', record.module)
        log_record.setdefault('correlation_id', getattr(record, 'correlation_id', '-'))
        if record.exc_info:
            log_record.setdefault('exception', self.formatException(record.exc_info))


def ensure_logs_dir(base_dir: Path) -> Path:
    logs_dir = base_dir / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir
