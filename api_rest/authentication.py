from __future__ import annotations

from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken

from .models import User


def _extract_user_identifier(payload: dict) -> str | None:
    for key in ('user_nickname', 'user_id', 'sub', 'username'):
        value = payload.get(key)
        if value:
            return str(value)
    return None


def get_user_from_token(raw_token: str) -> User:
    try:
        validated_token = UntypedToken(raw_token)
    except (InvalidToken, TokenError) as exc:
        raise AuthenticationFailed('Token JWT invalido.') from exc

    payload = getattr(validated_token, 'payload', validated_token)
    identifier = _extract_user_identifier(payload)
    if not identifier:
        raise AuthenticationFailed('Token JWT sem identificador de usuario.')

    try:
        return User.objects.get(pk=identifier)
    except User.DoesNotExist as exc:
        raise AuthenticationFailed('Usuario nao encontrado.') from exc


class JWTAuthentication(BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request):
        header = get_authorization_header(request).split()
        if not header:
            return None

        if header[0].lower() != self.keyword.lower().encode():
            return None

        if len(header) != 2:
            raise AuthenticationFailed('Cabecalho Authorization invalido.')

        raw_token = header[1].decode('utf-8')
        user = get_user_from_token(raw_token)
        return user, raw_token
