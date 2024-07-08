"""Ограничения доступа."""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Автор может менять, для других только чтение."""

    def has_permission(self, request, view):
        """Проверка права для пользователя."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Проверка права для объекта."""
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
