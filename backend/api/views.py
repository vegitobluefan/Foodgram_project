from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .paginators import CustomHomePagination
from .permissions import IsAuthenticatedAndAdminOrAuthorOrReadOnly
from .serializers import (CreateUpdateRecipeSerializer,
                          FavoriteRecipeSerializer, IngredientSerializer,
                          ReadOnlyRecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)
from .utils import delete_method, post_method


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ('get',)
    pagination_class = None
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ('get',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Recipe."""

    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete',)
    permission_classes = (IsAuthenticatedAndAdminOrAuthorOrReadOnly,)
    pagination_class = CustomHomePagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadOnlyRecipeSerializer
        return CreateUpdateRecipeSerializer

    @action(
        detail=True,
        url_path=r'(?P<id>\d+)/shopping_cart',
        methods=('post', 'delete',),
        serializer_class=ShoppingCartSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('id'))
        if request.method == 'POST':
            return post_method(request, recipe, ShoppingCartSerializer)

        if request.method == 'DELETE':
            return delete_method(request, recipe, ShoppingCart)

        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Ваша корзина:\n']

        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {measurement_unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="downloaded_shopping_cart.txt"')
        return response

    @action(
        detail=True,
        methods=('post', 'delete',),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('id'))
        if request.method == 'POST':
            return post_method(request, recipe, FavoriteRecipeSerializer)

        if request.method == 'DELETE':
            return delete_method(request, recipe, FavoriteRecipe)

        return Response(status=status.HTTP_404_NOT_FOUND)
