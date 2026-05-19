import json
import logging
from typing import Any

import redis
from django.conf import settings

logger = logging.getLogger(__name__)


def get_redis_client() -> redis.Redis:
    redis_settings = settings.REDIS
    return redis.Redis(
        host=redis_settings['HOST'],
        port=redis_settings['PORT'],
        db=redis_settings['DB'],
        password=redis_settings['PASSWORD'],
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )


class EventCacheService:
    # TTLs separados deixam o cache de item mais estavel que a listagem agregada.
    def __init__(self, client: redis.Redis | None = None):
        self.client = client or get_redis_client()
        self.prefix = settings.REDIS['KEY_PREFIX']
        self.item_ttl = settings.REDIS['ITEM_TTL_SECONDS']
        self.list_ttl = settings.REDIS['LIST_TTL_SECONDS']

    def item_key(self, event_id: int | str) -> str:
        return f'{self.prefix}event:item:{event_id}'

    def list_key(self, suffix: str = 'all') -> str:
        return f'{self.prefix}event:list:{suffix}'

    def get_event(self, event_id: int | str) -> dict[str, Any] | None:
        key = self.item_key(event_id)
        payload = self.client.get(key)
        if payload is None:
            logger.info('CACHE MISS: %s', key)
            return None

        logger.info('CACHE HIT: %s', key)
        return json.loads(payload)

    def set_event(self, event_id: int | str, data: dict[str, Any]) -> None:
        key = self.item_key(event_id)
        self.client.set(name=key, value=json.dumps(data), ex=self.item_ttl)
        logger.info('CACHE SET: %s ttl=%ss', key, self.item_ttl)

    def get_event_list(self, suffix: str = 'all') -> list[dict[str, Any]] | None:
        key = self.list_key(suffix)
        payload = self.client.get(key)
        if payload is None:
            logger.info('CACHE MISS: %s', key)
            return None

        logger.info('CACHE HIT: %s', key)
        return json.loads(payload)

    def set_event_list(self, data: list[dict[str, Any]], suffix: str = 'all') -> None:
        key = self.list_key(suffix)
        self.client.set(name=key, value=json.dumps(data), ex=self.list_ttl)
        logger.info('CACHE SET: %s ttl=%ss', key, self.list_ttl)

    def invalidate_event(self, event_id: int | str) -> None:
        item_key = self.item_key(event_id)
        removed = self.client.delete(item_key)
        self.invalidate_event_lists()
        logger.info('CACHE INVALIDATED: %s removed=%s', item_key, removed)

    def invalidate_event_lists(self) -> int:
        pattern = f'{self.prefix}event:list:*'
        removed = 0
        for key in self.client.scan_iter(match=pattern):
            removed += self.client.delete(key)

        logger.info('CACHE INVALIDATED: pattern=%s removed=%s', pattern, removed)
        return removed

    def ping(self) -> bool:
        return bool(self.client.ping())
