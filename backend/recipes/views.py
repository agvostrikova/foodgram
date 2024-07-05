"""View сlass рецепты."""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
# from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from django_short_url.views import get_surl
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# from api.constants import LEN_SHORT_URL
from api.filters import IngredientFilter, RecipeFilter, TagFilter
from api.paginations import LimitPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeSerializer, ShoppingCartSerializer,
                             TagSerializer)
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обработки запросов на получение ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обработки запросов на получение тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filterset_class = TagFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с рецептами.

    Обработка запросов создания/получения/редактирования/удаления рецептов
    Добавление/удаление рецепта в избранное и список покупок.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitPagination

    def action_post_delete(self, pk, serializer_class):
        """Удаление рецептов."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = serializer_class.Meta.model.objects.filter(
            user=user, recipe=recipe
        )

        if self.request.method == 'POST':
            serializer = serializer_class(
                data={'user': user.id, 'recipe': pk},
                context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if object.exists():
                object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Этого рецепта нет в списке'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        """Избранное."""
        return self.action_post_delete(pk, FavoriteSerializer)

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        """Корзина покупок."""
        return self.action_post_delete(pk, ShoppingCartSerializer)

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачать корзину покупок."""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            "attachment; filename='shopping_cart.pdf'"
        )
        p = canvas.Canvas(response)
        arial = ttfonts.TTFont('Arial', 'data/arial.ttf')
        pdfmetrics.registerFont(arial)
        p.setFont('Arial', 14)

        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user).values_list(
            'ingredient__name', 'amount', 'ingredient__measurement_unit')

        ingr_list = {}
        for name, amount, unit in ingredients:
            if name not in ingr_list:
                ingr_list[name] = {'amount': amount, 'unit': unit}
            else:
                ingr_list[name]['amount'] += amount
        height = 700

        p.drawString(100, 750, 'Список покупок')
        for i, (name, data) in enumerate(ingr_list.items(), start=1):
            p.drawString(
                80, height,
                f"{i}. {name} – {data['amount']} {data['unit']}")
            height -= 25
        p.showPage()
        p.save()
        return response

    @action(
        methods=['GET'],
        detail=True,
        permission_classes=(AllowAny,),
        url_path='(?P<pk>[^/.]+)/get-link',
    )
    def get_short_link(self, request, pk=None):
        """Получение коротких ссылок."""
        data = get_surl(request.build_absolute_uri())
        return Response({'short-link': data}, status=status.HTTP_200_OK)
        # recipe = get_object_or_404(Recipe, pk=pk)
        # protocol = request.scheme
        # domain = request.get_host()
        # surl = get_surl(
        #    reverse('api:recipes-detail', args=[recipe.id]).replace(
        #        'api/', ''
        #    ),
        #    length=LEN_SHORT_URL,
        # )
        # short_link = f'{protocol}://{domain}{surl}'
        # return Response(
        # {'short-link': short_link}, status=status.HTTP_200_OK)
