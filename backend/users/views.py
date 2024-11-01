from api.serializers import (AvatarSerializer, UserGetSubscribeSerializer,
                             UserSerializer)
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .models import MyUser, SubscriptionUser


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
        detail=False, methods=('get'), permission_classes=(IsAuthenticated,),)
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=True, methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),)
    def subscribe(self, request, id=None):
        subscriber = self.request.user
        author = get_object_or_404(MyUser, pk=id)

        if request.method == 'POST':
            serializer = UserGetSubscribeSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            SubscriptionUser.objects.create(user=subscriber, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(
                SubscriptionUser, user=subscriber, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

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


class UserSubscriptionsViewSet(mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    """Получение списка всех подписок на пользователей."""
    serializer_class = UserGetSubscribeSerializer

    def get_queryset(self):
        return MyUser.objects.filter(author__user=self.request.user)
