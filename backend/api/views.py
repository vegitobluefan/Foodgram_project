from rest_framework import viewsets, permissions

from recipes.models import Ingredient, Recipe, Tag
from .permissions import IsAuthenticatedAndAdminOrAuthorOrReadOnly
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer
from .paginators import CustomHomePagination


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
