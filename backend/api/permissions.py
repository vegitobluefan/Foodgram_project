from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Права доступа для админа."""

    def has_permission(self, request, view):
        return request.user.is_admin


class IsAuthenticatedAndAdminOrAuthorOrReadOnly(permissions.BasePermission):
    """Аутентифицирован, автор, админ, модератор."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
            or request.user.is_admin
            or request.user.is_moderator
        )


class IsAuthenticatedAndAdminOrSuperuserOrReadOnly(permissions.BasePermission):
    """Аутентифицирован, автор или суперюзер."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )
