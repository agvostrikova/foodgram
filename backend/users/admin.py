"""Настройки админ панели."""

from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin

from users.models import Follow, User


@register(User)
class CustomUserAdmin(UserAdmin):
    """Пользователь."""

    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')


@register(Follow)
class FollowAdmin(ModelAdmin):
    """Подписки."""

    list_display = ('user', 'author')
