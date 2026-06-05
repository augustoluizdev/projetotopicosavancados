from rest_framework.permissions import BasePermission


def _is_authenticated_user(user):
    return bool(user and getattr(user, 'is_authenticated', False) and hasattr(user, 'user_nickname'))


class IsAdminUser(BasePermission):
    """
    Permissao customizada para verificar se o usuario e administrador.
    """

    message = 'Apenas usuarios administradores podem executar esta acao.'

    def has_permission(self, request, view):
        return _is_authenticated_user(request.user) and getattr(request.user, 'is_admin', False)


class IsOwnerOrReadOnly(BasePermission):
    """
    Permissao para que o usuario so possa editar seus proprios dados.
    """

    message = 'Voce so pode editar seus proprios dados.'

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, 'is_admin', False):
            return True

        if not _is_authenticated_user(request.user):
            return False

        if hasattr(obj, 'user_nickname'):
            return obj.user_nickname == request.user.user_nickname

        if hasattr(obj, 'user'):
            return obj.user.user_nickname == request.user.user_nickname

        return False


class IsOwnerOrAdmin(BasePermission):
    """
    Permite acesso somente ao dono do recurso ou a um administrador.
    """

    message = 'Voce so pode acessar seus proprios dados.'

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, 'is_admin', False):
            return True

        if not _is_authenticated_user(request.user):
            return False

        if hasattr(obj, 'user_nickname'):
            return obj.user_nickname == request.user.user_nickname

        if hasattr(obj, 'user'):
            return obj.user.user_nickname == request.user.user_nickname

        if hasattr(obj, 'user_id'):
            return obj.user_id == request.user.user_nickname

        return False


class IsAdminOrReadOnly(BasePermission):
    """
    Permissao para que apenas admins possam criar/editar eventos.
    Usuarios normais podem apenas ler.
    """

    message = 'Apenas administradores podem executar esta acao.'

    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        return _is_authenticated_user(request.user) and getattr(request.user, 'is_admin', False)


class IsAuthenticatedUser(BasePermission):
    """
    Permissao para verificar se o usuario esta autenticado.
    Funciona com o sistema customizado de autenticacao da API.
    """

    message = 'Voce precisa estar autenticado para executar esta acao.'

    def has_permission(self, request, view):
        return _is_authenticated_user(request.user)
