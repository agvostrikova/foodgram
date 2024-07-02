"""Фильтры API."""

from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


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

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug', to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        """class Meta RecipeFilter."""

        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр избранного."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр списка покупок."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class TagFilter(FilterSet):
    """Фильтр тегов."""

    class Meta:
        """class Meta фильтров тега."""

        model = Tag
        fields = ('name', 'slug')
