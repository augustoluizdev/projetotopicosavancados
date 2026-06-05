from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from .authentication import get_user_from_token


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        token = self._get_token(scope)

        if token:
            scope['user'] = await get_user_from_jwt(token)
        else:
            scope['user'] = scope.get('user', AnonymousUser())

        return await self.app(scope, receive, send)

    def _get_token(self, scope):
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        tokens = query_params.get('token')

        if not tokens:
            return None

        return tokens[0]


@database_sync_to_async
def get_user_from_jwt(token):
    try:
        return get_user_from_token(token)
    except Exception:
        return AnonymousUser()
