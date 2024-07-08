"""Сериалайзеры."""

import base64

from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow, User


class UsersCreateSerializer(UserCreateSerializer):
    """Сериализатор для обработки запросов на создание пользователя."""

    class Meta:
        """class Meta создание пользователя."""

        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value):
        """Проверка пользователя с именем me."""
        if value == "me":
            raise ValidationError(
                'Невозможно создать пользователя с таким именем!'
            )
        return value

    def create(self, validated_data: dict) -> User:
        """Создаёт нового пользователя с запрошенными полями."""
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для кодирования изображения в base64."""

    def to_internal_value(self, data):
        """Кодирование изображения."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)


class UserAvatarSerializer(serializers.Serializer):
    """Сериализатор для аватара пользователя."""

    avatar = Base64ImageField(allow_null=True, required=True)

    def update(self, instance, validated_data):
        """Обновление аватара."""
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class UsersSerializer(UserSerializer):
    """Сериализатор для отображения информации о пользователе."""

    is_subscribed = SerializerMethodField(read_only=True)
    avatar = Base64ImageField(allow_null=True, required=False)

    class Meta:
        """class Meta отображение информации о пользователи."""

        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, object):
        """Проверка подписки пользователя на автора."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=object.id).exists()

    def get_avatar(self, obj):
        """Ссылка на аватар."""
        if obj.avatar:
            return obj.avatar.url
        return None


class FollowSerializer(UsersSerializer):
    """Сериализатор для добавления/удаления подписки, просмотра подписок."""

    recipes = SerializerMethodField(read_only=True)
    recipes_count = SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        """Meta class подписки."""

        fields = UsersSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def get_recipes(self, object):
        """Возвращает рецепты пользователя."""
        request = self.context.get('request')
        context = {'request': request}
        recipe_limit = request.query_params.get('recipes_limit')
        queryset = object.recipes.all()
        if recipe_limit:
            queryset = queryset[:int(recipe_limit)]
        return RecipeInfoSerializer(queryset, context=context, many=True).data

    def get_recipes_count(self, object):
        """Возвращает количество рецептов пользователя."""
        return object.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с тегами."""

    class Meta:
        """Meta class тега."""

        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами."""

    class Meta:
        """Meta class ингредиента."""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для подробного описания ингредиентов в рецепте."""

    name = serializers.CharField(
        source='ingredient.name', read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        """Meta class ингредиентов."""

        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиента при создании рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient')

    class Meta:
        """Meta class ингредиентов."""

        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания рецепта.

    Валидирует ингредиенты ответ возвращает GetRecipeSerializer.
    """

    author = UsersSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(many=True)

    class Meta:
        """Meta class рецептов."""

        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def validate(self, data):
        """Валидация тегов и ингредиентов."""
        required_fields = (
            'ingredients',
            'tags',
            'name',
            'text',
            'cooking_time',
        )
        for field in required_fields:
            if field not in data:
                raise ValidationError({field: 'Обязательное поле'})

        list_ingr = [item['ingredient'] for item in data['ingredients']]
        all_ingredients, distinct_ingredients = (
            len(list_ingr), len(set(list_ingr)))

        if all_ingredients != distinct_ingredients:
            raise ValidationError(
                {'error': 'Ингредиенты должны быть уникальными'}
            )
        if not data['ingredients']:
            raise ValidationError(
                {'error': 'Должен быть, хотя бы один игридиент'}
            )
        if len(data['tags']) != len(set(data['tags'])):
            raise ValidationError(
                {'error': 'Теги не должны повторяться'}
            )
        return data

    def get_ingredients(self, recipe, ingredients):
        """Получение ингредиентов."""
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients)

    @transaction.atomic
    def create(self, validated_data):
        """Создание рецепта."""
        user = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=user,
                                       **validated_data)
        recipe.tags.set(tags)
        self.get_ingredients(recipe, ingredients)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновление рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        RecipeIngredient.objects.filter(recipe=instance).delete()

        instance.tags.set(tags)
        self.get_ingredients(instance, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Отображение полной информации рецепта."""
        context = {'request': self.context.get('request')}
        return GetRecipeSerializer(instance, context=context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого отображения рецепта."""

    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        """Получить картинку рецепта."""
        return obj.image.url

    class Meta:
        """Meta class краткое отображение рецепта."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)


class RecipeForUserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя с рецептами."""

    class Meta:
        """Meta class рецетов."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения полной информации о рецепте."""

    tags = TagSerializer(many=True)
    author = UsersSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(read_only=True, many=True,
                                             source='recipe_ingredient')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Meta class полная информация рецепта."""

        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, object):
        """Получить избранный рецепт."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return object.favorite.filter(user=user).exists()

    def get_is_in_shopping_cart(self, object):
        """Получить корзину пользователя."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return object.shopping_cart.filter(user=user).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор добавления/удаления рецепта в избранное."""

    class Meta:
        """Meta class рецепт в избранном."""

        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        """Валидация на сущестования рецепта."""
        user, recipe = data.get('user'), data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                {'error': 'Этот рецепт уже добавлен'}
            )
        return data

    def to_representation(self, instance):
        """Отображение краткой информации рецепта."""
        context = {'request': self.context.get('request')}
        return RecipeInfoSerializer(instance.recipe, context=context).data


class ShoppingCartSerializer(FavoriteSerializer):
    """Сериализатор добавления/удаления рецепта в список покупок."""

    class Meta(FavoriteSerializer.Meta):
        """Meta class списка покупок."""

        model = ShoppingCart


class RecipeInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения краткой информации о рецепте."""

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        """Meta class краткой информации."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
