from .serializers import MyUserSerializer, UserSubscribeSerializer
from api.paginators import CustomHomePagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import MyUser


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели User."""

    serializer_class = MyUserSerializer
    queryset = MyUser.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = DjangoFilterBackend
    lookup_field = 'username'
    search_fields = ['username', ]
    http_method_names = ('get', 'post', 'head', 'patch', 'delete',)

    @action(
        detail=True, methods=('get',), permission_classes=(IsAuthenticated,),
        url_name='avatar'
    )
    def avatar(self, request):
        serializer = MyUserSerializer(request.user)
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )


class SubscriptionListView(ListAPIView):
    serializer_class = UserSubscribeSerializer
    pagination_class = CustomHomePagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        current_user = self.request.user
        queryset = MyUser.objects.filter(author__subscriber=current_user)

        return queryset
