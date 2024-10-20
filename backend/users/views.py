from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import MyUser
from .serializers import MyUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели User."""

    serializer_class = MyUserSerializer
    queryset = MyUser.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = DjangoFilterBackend
    lookup_field = 'username'
    search_fields = ['username', ]
    http_method_names = ('get', 'post', 'head', 'patch', 'delete',)

    @action(methods=['patch', 'get'], detail=False,
            permission_classes=[IsAuthenticated, ])
    def me(self, request):
        if request.method == 'GET':
            serializer = MyUserSerializer(self.request.user)
        else:
            serializer = MyUserSerializer(
                self.request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def avatar(self, request, pk=None):
        serializer = MyUserSerializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
