from django.db.models import Sum
from django.shortcuts import get_object_or_404
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .paginators import CustomHomePagination
from .permissions import IsAuthenticatedAndAdminOrAuthorOrReadOnly
from .serializers import (CreateUpdateRecipeSerializer,
                          FavoriteRecipeSerializer, IngredientSerializer,
                          ReadOnlyRecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)
from .utils import delete_method, download_cart, post_method


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    search_fields = ('^name',)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = CreateUpdateRecipeSerializer
    permission_classes = (IsAuthenticatedAndAdminOrAuthorOrReadOnly,)
    pagination_class = CustomHomePagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadOnlyRecipeSerializer
        return CreateUpdateRecipeSerializer

    @action(
        detail=True, methods=('post', 'delete',),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return post_method(request, recipe, ShoppingCartSerializer)

        if request.method == 'DELETE':
            return delete_method(request, recipe, ShoppingCart)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=True, methods=('post',), permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteRecipeSerializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        get_object_or_404(
            FavoriteRecipe, user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__cart_recipe__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_sum=Sum('amount'))
        return download_cart(ingredients)

    @action(
        methods=('get',), detail=True,
        url_path='get-link',
        url_name='get-link',
    )
    def get_link(self, request, pk=None):
        pass
