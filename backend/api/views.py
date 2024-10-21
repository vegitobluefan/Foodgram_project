from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .paginators import CustomHomePagination
from .permissions import IsAuthenticatedAndAdminOrAuthorOrReadOnly
from .serializers import (CreateUpdateRecipeSerializer,
                          FavoriteShopListSerializer, IngredientSerializer,
                          ReadOnlyRecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ('get')
    pagination_class = None
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ('get')


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Recipe."""

    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthenticatedAndAdminOrAuthorOrReadOnly,)
    pagination_class = CustomHomePagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadOnlyRecipeSerializer
        return CreateUpdateRecipeSerializer

    @action(
        detail=False,
        url_path=r'(?P<id>\d+)/shopping_cart',
        methods=['post', 'delete'],
        serializer_class=ShoppingCartSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('id'))
        favorite = ShoppingCart.objects.filter(
            recipe=recipe, user=request.user,)

        if request.method == 'POST':
            if not favorite.exists():
                ShoppingCart.objects.create(
                    recipe=recipe, user=request.user,
                )
                serializer = FavoriteShopListSerializer(instance=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
