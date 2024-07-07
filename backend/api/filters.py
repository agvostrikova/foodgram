"""Фильтры API."""

from django.db.models import (BooleanField, Exists, ExpressionWrapper, Q,
                              OuterRef)
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag, Favorite, ShoppingCart


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов по названию."""

    name = filters.CharFilter(method='filter_name')

    class Meta:
        """class Meta фильтра ингредиентов по названию."""

        model = Ingredient
        fields = ('name',)

    def filter_name(self, queryset, name, value):
        """Метод возвращает кверисет с заданным именем ингредиента."""
        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        ).annotate(
            startswith=ExpressionWrapper(
                Q(name__istartswith=value),
                output_field=BooleanField()
            )
        ).order_by('-startswith')


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
        if value:
            return queryset.filter(
                Exists(
                    Favorite.objects.filter(
                        user=self.request.user, recipe=OuterRef('pk')
                    )
                )
            )
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр списка покупок."""
        if not self.request.user.is_authenticated:
            return queryset.none()
        if value:
            return queryset.filter(
                Exists(
                    ShoppingCart.objects.filter(
                        user=self.request.user, recipe=OuterRef('pk')
                    )
                )
            )
        return queryset


class TagFilter(FilterSet):
    """Фильтр тегов."""

    class Meta:
        """class Meta фильтров тега."""

        model = Tag
        fields = ('name', 'slug')
