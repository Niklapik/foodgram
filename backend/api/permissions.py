from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import permissions

from django.contrib.auth import get_user_model

User = get_user_model()


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешает безопасные методы (GET, HEAD, OPTIONS) всем,
    остальные методы — только администраторам.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешение только для автора или только на чтение."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
                request.method in permissions.SAFE_METHODS
                or obj.author == request.user
        )
