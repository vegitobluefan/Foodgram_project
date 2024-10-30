from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .models import MyUser, SubscriptionUser
from .serializers import (AvatarSerializer, UserGetSubscribeSerializer,
                          UserSerializer)


class MyUserViewSet(UserViewSet):
    """Вьюсет для модели User."""

    serializer_class = UserSerializer
    queryset = MyUser.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_context_data(self):
        context = super().get_context_data()
        context['request'] = self.request
        return context

    def change_avatar(self, data):
        instance = self.get_instance()
        serializer = AvatarSerializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

    @action(
        detail=False, methods=('get'), permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=True, methods=('put',), permission_classes=(IsAuthenticated,),
    )
    def avatar(self, request, id=None):
        serializer = self.change_avatar(request.data)
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request, id=None):
        data = request.data
        if 'avatar' not in data:
            data = {'avatar': None}
        self.change_avatar(data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = MyUser.objects.filter(following__username=user)
        pages = self.paginate_queryset(queryset)
        serializer = UserGetSubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        subscriber = self.request.user
        author = get_object_or_404(MyUser, pk=id)
        sub_existence = SubscriptionUser.objects.filter(
            user=subscriber, author=author
        ).exists()

        if self.request.method == 'POST':
            if subscriber == author:
                raise ValidationError(
                    'Нельзя подписываться на самого себя.')
            if sub_existence:
                raise ValidationError(
                    'Вы уже подписаны на этого автора.')
            SubscriptionUser.objects.create(user=subscriber, author=author)
            serializer = UserGetSubscribeSerializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not sub_existence:
                raise ValidationError(
                    'Вы не подписаны на данного пользователя.')
            subscription = get_object_or_404(
                SubscriptionUser, user=subscriber, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
