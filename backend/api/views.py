from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from rest_framework import status, viewsets, exceptions
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
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
    # filter_backends = DjangoFilterBackend

    def get_serializer_class(self):
        if self.request.method in ('create', 'update', 'partial_update'):
            return CreateUpdateRecipeSerializer
        return ReadOnlyRecipeSerializer

    @action(
        detail=True,
        methods=('post', 'delete',),
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
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_list__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return self.send_message(ingredients)

    @action(
        detail=True, methods=('post', 'delete',),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('id'))
        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                raise exceptions.ValidationError(
                    'Рецепт уже добавлен в избранное.'
                )
            FavoriteRecipe.objects.create(user=request.user, recipe=recipe)
            serializer = FavoriteRecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not FavoriteRecipe.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                raise exceptions.ValidationError(
                    'Рецепта нет в избранном.'
                )
            favorite = get_object_or_404(
                FavoriteRecipe,
                user=request.user,
                recipe=recipe
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
