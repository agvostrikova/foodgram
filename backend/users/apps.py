"""Приложение Пользователь."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Класс приложения Пользователя."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
