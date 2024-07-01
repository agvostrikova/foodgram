from django.shortcuts import get_object_or_404

from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from api.serializers import (
    FollowSerializer, UsersSerializer, UserAvatarSerializer
)
from api.paginations import LimitPagination
from users.models import Follow, User


class UsersViewSet(UserViewSet):
    """Вьюсет для работы с пользователями и подписками.
    Обработка запросов на создание/получение пользователей и
    создание/получение/удаления подписок."""

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitPagination
    http_method_names = ['get', 'post', 'delete', 'head', 'put']

    @action(methods=['POST', 'DELETE'],
            detail=True, )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Follow.objects.filter(
            user=user, author=author)

        if request.method == 'POST':
            if subscription.exists():
                return Response({'error': 'Вы уже подписаны'},
                                status=status.HTTP_400_BAD_REQUEST)
            if user == author:
                return Response({'error': 'Невозможно подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowSerializer(author, context={'request': request})
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Вы не подписаны на этого пользователя'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        follows = User.objects.filter(following__user=user)
        page = self.paginate_queryset(follows)
        serializer = FollowSerializer(
            page, many=True,
            context={'request': request},
        )

        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        methods=('PUT', 'DELETE', ),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar',
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = UserAvatarSerializer(
                user, data=request.data)
        if request.method == 'DELETE':
            user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
