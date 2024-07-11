"""Фильтры API."""

from django.db.models import Q
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов по названию."""

    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        """class Meta IngredientFilter."""

        model = Ingredient
        fields = ('name', )


class RecipeFilter(FilterSet):
    """Фильтр рецептов по автору/тегу/подписке/наличию в списке покупок."""

    tags = filters.CharFilter(method='filter_tags')
    author = filters.NumberFilter(field_name='author__id')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        """class Meta RecipeFilter."""

        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_tags(self, queryset, name, value):
        """Фильтрация по нескольким тегам, переданным через параметр 'tags'."""
        tags = self.request.query_params.getlist('tags')
        if tags:
            query = Q()
            for tag in tags:
                query |= Q(tags__slug=tag)
            queryset = queryset.filter(query).distinct()
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр избранного."""
        if not self.request.user.is_authenticated:
            return queryset.none()
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр списка покупок."""
        if not self.request.user.is_authenticated:
            return queryset.none()
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class TagFilter(FilterSet):
    """Фильтр тегов."""

    class Meta:
        """class Meta фильтров тега."""

        model = Tag
        fields = ('name', 'slug')
