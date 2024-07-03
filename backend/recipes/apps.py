"""Приложение Рецепты."""

from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Класс приложения Рецепты."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
