from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, views, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User
from .serializers import MyUserSerializer  # MyUserCreateSerializer,


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели User."""

    serializer_class = MyUserSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = DjangoFilterBackend
    lookup_field = 'username'
    search_fields = ['username', ]
    http_method_names = ('get', 'post', 'head', 'patch', 'delete',)

    @action(methods=['patch', 'get'], detail=False,
            permission_classes=[permissions.IsAuthenticated, ])
    def me(self, request):
        if request.method == 'GET':
            serializer = MyUserSerializer(self.request.user)
        else:
            serializer = MyUserSerializer(
                self.request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthView(views.APIView):
    """Класс для получения токена"""

    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        user = authenticate(
            email=request.data['email'], password=request.data['password']
        )
        if user:
            token, created = Token.objets.get_or_create(user=user)
            return Response({'auth_token': token.key})
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
