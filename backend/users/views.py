from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import authentication, permissions, status, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import User
from .serializers import MyUserCreateSerializer, MyUserSerializer


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
            permission_classes=[permissions.IsAuthenticated,])
    def me(self, request):
        if request.method == 'GET':
            serializer = MyUserSerializer(self.request.user)
        else:
            serializer = MyUserSerializer(
                self.request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def registration(request):
    """Функция для регистрации."""

    user = MyUserCreateSerializer(data=request.data)
    user.is_valid(raise_exception=True)
    email = user.data['email']
    username = user.data['username']
    data = user.data

    user, created = User.objects.get_or_create(
        email=email,
        username=username)

    confirmation_code = default_token_generator.make_token(user)

    send_mail(
        subject='Confirmation code',
        message=f"Your code - {confirmation_code}",
        from_email=None,
        recipient_list=[email],
        fail_silently=False
    )
    return Response(
        data,
        status=status.HTTP_200_OK
    )


class AuthView(views.APIView):
    """Класс для получения токена"""

    authentication_classes = (authentication.TokenAuthentication,)

    def post(self, request):
        user = authenticate(
            email=request.data['email'], password=request.data['password']
        )
        if user:
            token, created = Token.objets.get_or_create(user=user)
            return Response({'auth_token': token.key})
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
