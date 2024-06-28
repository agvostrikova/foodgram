from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from api.filters import IngredientFilter, RecipeFilter, TagFilter
from api.paginations import LimitPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    RecipeWriteSerializer, IngredientSerializer,
    RecipeReadSerializer, ShortRecipeSerializer,
    TagSerializer
)
from recipes.models import (
    Ingredient, Recipe, RecipeIngredient, Tag, Favorite, ShoppingCart
)


def pdf_generation(value_list):
    final_list = {}
    for item in value_list:
        name = item[0]
        if name not in final_list:
            final_list[name] = {
                'measurement_unit': item[1],
                'amount': item[2]
            }
        else:
            final_list[name]['amount'] += item[2]
    pdfmetrics.registerFont(
        TTFont('Halogen', 'Halogen.ttf', 'UTF-8'))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; '
        'filename="shopping_list.pdf"'
    )
    page = canvas.Canvas(response)
    page.setFont('Halogen', size=24)
    page.drawString(200, 800, 'Список ингредиентов')
    page.setFont('Halogen', size=16)
    height = 750
    for i, (name, data) in enumerate(final_list.items(), 1):
        page.drawString(75, height, (f'<{i}> {name} - {data["amount"]}, '
                                     f'{data["measurement_unit"]}'))
        height -= 25
    page.showPage()
    page.save()
    return response


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
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_obj(Favorite, request.user, pk)
        if request.method == 'DELETE':
            return self.delete_obj(Favorite, request.user, pk)
        return None

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_obj(ShoppingCart, request.user, pk)
        if request.method == 'DELETE':
            return self.delete_obj(ShoppingCart, request.user, pk)
        return None

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart_recipe__user=request.user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'amount')
        return pdf_generation(ingredients)

    def delete_obj(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'errors': 'Рецепт уже удален'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def add_obj(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({
                'errors': 'Рецепт уже добавлен в список'
            }, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

#    @action(
#        methods=('GET', ),
#        detail=False,
#        permission_classes=(IsAuthenticated,),
#        url_path='(?P<recipe_id>[^/.]+)/get-link',
#    )
#    def shorten(request, url):
#        #pyshorteners.Shortener().tinyurl.short(url)
#        return Response({"short-link": 'Привет'}, status=status.HTTP_200_OK)