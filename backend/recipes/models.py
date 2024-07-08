"""Models  рецептов."""

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from api.constants import (AMOUNT_LIMIT, MAX_LEN_NAME_INGREDIENT,
                           MAX_LEN_NAME_RECIPE, MAX_LEN_NAME_SLUG,
                           MAX_LEN_NAME_TAG, MAX_LEN_NAME_UNIT,
                           MAX_LEN_SHORT_CODE)

User = get_user_model()


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=MAX_LEN_NAME_TAG,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=MAX_LEN_NAME_SLUG,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        """Meta class теги."""

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        """Строковое представление."""
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        max_length=MAX_LEN_NAME_INGREDIENT,
        verbose_name='Ингредиент',
    )
    measurement_unit = models.CharField(
        max_length=MAX_LEN_NAME_UNIT,
        verbose_name='Единица измерения'
    )

    class Meta:
        """Meta class ингредиентов."""

        ordering = ('name',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingredient')
        ]

    def __str__(self):
        """Строковое представление."""
        return self.name


class Recipe(models.Model):
    """Модель рецепт."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient',
        related_name='recipe'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка'
    )
    name = models.CharField(
        max_length=MAX_LEN_NAME_RECIPE,
        verbose_name='Название'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(MinValueValidator(
            limit_value=1,
            message='Время приготовления не может быть менее одной минуты.'),
        )
    )
    is_favorited = models.ManyToManyField(
        User,
        verbose_name='Понравившиеся рецепты',
        related_name='is_favorited',
        blank=True,
    )
    is_in_shopping_cart = models.ManyToManyField(
        User,
        related_name='is_in_shopping_cart',
        verbose_name='Список покупок',
        blank=True,
    )
    short_code = models.CharField(
        max_length=MAX_LEN_SHORT_CODE, unique=True, blank=True, null=True
    )
    pub_date = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        """Meta class рецепт."""

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        """Строковое представление."""
        return self.name


class RecipeIngredient(models.Model):
    """Модель рецепт+ингредиент."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredient_recipes',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(MinValueValidator(
            limit_value=AMOUNT_LIMIT,
            message='Количество должно быть больше нуля'),
        )
    )

    class Meta:
        """Meta class  ингредиентов."""

        verbose_name = 'Список ингредиентов'
        verbose_name_plural = 'Списки ингредиентов'
        constraints = [
            UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique ingredient for recipe'
            )
        ]

    def __str__(self):
        """Строковое представление."""
        return (f'{self.recipe}: {self.ingredient.name},'
                f' {self.amount}, {self.ingredient.measurement_unit}')


class Favorite(models.Model):
    """Модель избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='favorite'
    )

    class Meta:
        """Meta class  избранное."""

        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique favorite'
            ),
        )

    def __str__(self):
        """Строковое представление."""
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    """Модель корзины покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='shopping_cart'
    )

    class Meta:
        """Meta class  корзины покупок."""

        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique recipe in shopping cart'
            ),
        )

    def __str__(self):
        """Строковое представление."""
        return f'{self.recipe} в корзине у {self.user}'
