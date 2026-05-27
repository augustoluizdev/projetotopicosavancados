from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from .models import User


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
        from rest_framework_simplejwt.authentication import JWTAuthentication
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    except ImportError:
        return AnonymousUser()

    try:
        jwt_authentication = JWTAuthentication()
        validated_token = jwt_authentication.get_validated_token(token)
        payload = getattr(validated_token, 'payload', validated_token)
        user_identifier = (
            payload.get('user_nickname')
            or payload.get('user_id')
            or payload.get('sub')
            or payload.get('username')
        )

        if not user_identifier:
            return AnonymousUser()

        return User.objects.get(pk=str(user_identifier))
    except (InvalidToken, TokenError, User.DoesNotExist, ValueError, TypeError):
        return AnonymousUser()
