"""Ограничения доступа."""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Автор может менять, для других только чтение."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            or request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.method in permissions.SAFE_METHODS
        )
