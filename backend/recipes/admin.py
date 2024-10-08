"""Настройка админ панеди рецептов."""
from django.contrib.admin import ModelAdmin, register, TabularInline

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    """Ингридиенты."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@register(Tag)
class TagAdmin(ModelAdmin):
    """Теги."""

    list_display = ('name', 'slug')


class RecipeIngredientInline(TabularInline):
    """Рецепт+ингредиент."""

    model = RecipeIngredient
    extra = 0
    min_num = 1


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    """Рецепт."""

    list_display = (
        'name', 'author', 'pub_date', 'display_tags',
        'favorite'
    )
    inlines = [RecipeIngredientInline]
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name',)
    readonly_fields = ('favorite',)
    fields = (
        'image', ('name', 'author'),
        'text', ('tags', 'cooking_time'),
        'favorite'
    )

    def display_tags(self, obj):
        """Теги."""
        return ', '.join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = 'Теги'

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
