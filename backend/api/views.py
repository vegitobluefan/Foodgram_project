from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, Recipe, Tag, User
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .paginators import CustomHomePagination
from .permissions import IsAuthenticatedAndAdminOrAuthorOrReadOnly
from .serializers import (IngredientSerializer, MyUserCreateSerializer,
                          RecipeSerializer, TagSerializer,
                          UserAccessTokenSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedAndAdminOrAuthorOrReadOnly,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedAndAdminOrAuthorOrReadOnly,)


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Recipe."""

    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedAndAdminOrAuthorOrReadOnly,)
    pagination_class = CustomHomePagination


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
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


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    """Функция для получения токена"""

    serializer = UserAccessTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data["username"]
    user = get_object_or_404(User, username=username)
    token = AccessToken.for_user(user)
    return Response({'token': str(token)}, status=status.HTTP_200_OK)
