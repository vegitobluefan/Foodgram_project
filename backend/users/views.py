from api.paginators import CustomHomePagination
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .models import MyUser, SubscriptionUser
from .serializers import (MyUserSerializer, UserGetSubscribeSerializer,
                          UserPostDelSubscribeSerializer)


class UserViewSet(djoser_views.UserViewSet):
    """Вьюсет для модели User."""

    # serializer_class = MyUserSerializer
    # queryset = MyUser.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = DjangoFilterBackend
    lookup_field = 'username'
    search_fields = ('username', )
    # http_method_names = ('get', 'post', 'head', 'patch', 'delete',)

    @action(
        detail=False, methods=('get'),
        permission_classes=(IsAuthenticated,),
        url_name='me',
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=True, methods=('get',), permission_classes=(IsAuthenticated,),
        url_name='avatar'
    )
    def avatar(self, request):
        return Response(
            MyUserSerializer(request.user).data,
            status=status.HTTP_200_OK
        )


class SubscriptionListView(ListAPIView):
    serializer_class = UserGetSubscribeSerializer
    pagination_class = CustomHomePagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        current_user = self.request.user
        return MyUser.objects.filter(author__subscriber=current_user)


class SubscriptionPostDelView(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = UserGetSubscribeSerializer

    def post(self, request, user_id):
        subscribing_to = get_object_or_404(MyUser, pk=user_id)
        subscribing_to.save()
        subscriber = request.user

        serializer_subscribe = UserPostDelSubscribeSerializer(
            data={
                'subscribed_to': subscribing_to.id,
                'subscriber': subscriber.id,
            },
            context={'request': request}
        )
        serializer_subscribe.is_valid(raise_exception=True)
        serializer_subscribe.save()
        return Response(
            serializer_subscribe.data, status=status.HTTP_201_CREATED
        )

    def delete(self, request, user_id):
        subscribed_to = get_object_or_404(MyUser, pk=user_id)

        subscriptions = SubscriptionUser.objects.filter(
            subscriber=request.user,
            subscribed_to=subscribed_to
        )
        if not subscriptions.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscriptions.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
