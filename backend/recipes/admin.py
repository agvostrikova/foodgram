"""Настройка админ панеди рецептов."""
from django.contrib.admin import ModelAdmin, register

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    """Ингридиенты."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@register(Tag)
class TagAdmin(ModelAdmin):
    """Теги."""

    list_display = ('name', 'slug')


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    """Рецепт."""

    list_display = (
        'name', 'author', 'pub_date', 'display_tags', 'display_ingredients',
        'favorite'
    )
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name',)
    readonly_fields = ('favorite',)
    fields = ('image',
              ('name', 'author'),
              'ingredients'
              'text',
              ('tags', 'cooking_time'),
              'favorite')

    def display_tags(self, obj):
        """Теги."""
        return ', '.join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = 'Теги'

    def display_ingredients(self, obj):
        """Ингредиенты."""
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )
    display_ingredients.short_description = 'Ингредиенты'

    def favorite(self, obj):
        """Избранное."""
        return obj.favorite.count()
    favorite.short_description = 'Количество раз в избранном'


@register(RecipeIngredient)
class RecipeIngredientAdmin(ModelAdmin):
    """Рецепт+ингредиент."""

    list_display = ('recipe', 'ingredient', 'amount')


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    """Избранное."""

    list_display = ('recipe', 'user')


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    """Корзина покупок."""

    list_display = ('recipe', 'user')
