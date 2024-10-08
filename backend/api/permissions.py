from rest_framework import permissions


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
