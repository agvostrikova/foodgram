"""Models пользователя."""

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from rest_framework.exceptions import ValidationError

from api.constants import (MAX_LEN_EMAIL, MAX_LEN_FERST_NAME,
                           MAX_LEN_LAST_NAME, MAX_LEN_USERNAME)


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=MAX_LEN_EMAIL,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        max_length=MAX_LEN_USERNAME,
        validators=[
            RegexValidator(regex=r'^[\w.@+-]+\Z', )
        ]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LEN_FERST_NAME,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LEN_LAST_NAME,
    )
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        default='users/image.png',
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'last_name', 'first_name')

    class Meta:
        """Meta class Пользователя."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Строковое представление."""
        return self.username


class Follow(models.Model):
    """Модель подписчика."""

    user = models.ForeignKey(
        User,
        related_name='follower',
        verbose_name='Подписчик',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    def __str__(self):
        """Строковое представление."""
        return f'Автор: {self.author}, подписчик: {self.user}'

    def save(self, **kwargs):
        """Сохранение подписки."""
        if self.user == self.author:
            raise ValidationError("Невозможно подписаться на себя")
        super().save()

    class Meta:
        """Class Meta подписчика."""

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_follower')
        ]
