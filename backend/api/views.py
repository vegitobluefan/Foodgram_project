from django.db.models import Sum
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from foodgram.settings import RECIPE_LINK
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, SubscriptionUser, Tag, User)

from .filters import IngredientFilter, RecipeFilter
from .paginators import CustomHomePagination
from .serializers import (AvatarSerializer, CreateUpdateRecipeSerializer,
                          FavoriteRecipeSerializer, IngredientSerializer,
                          ReadOnlyRecipeSerializer, ShoppingCartSerializer,
                          TagSerializer, UserGetSubscribeSerializer,
                          UserSerializer)
from .utils import (download_cart, remove_from_shopping_cart_or_favorites,
                    to_shopping_cart_or_favorite)


class UserViewSet(UserViewSet):
    """Вьюсет для модели User."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_context_data(self):
        context = super().get_context_data()
        context['request'] = self.request
        return context

    def change_avatar(self, data):
        instance = self.get_instance()
        serializer = AvatarSerializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

    @action(
        detail=True, methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),)
    def subscribe(self, request, id=None):
        subscriber = self.request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            serializer = UserGetSubscribeSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            SubscriptionUser.objects.create(user=subscriber, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(
                SubscriptionUser, user=subscriber, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,),
            methods=('get'))
    def subscriptions(self, request):
        authors = self.paginate_queryset(
            User.objects.filter(subscribed_to__user=request.user)
        )
        serializer = UserGetSubscribeSerializer(
            authors, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=('put',), permission_classes=(IsAuthenticated,),
    )
    def avatar(self, request, id=None):
        serializer = self.change_avatar(request.data)
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request, id=None):
        data = request.data
        if 'avatar' not in data:
            data = {'avatar': None}
        self.change_avatar(data)
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientFilter,)
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
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filterset_class = RecipeFilter
    pagination_class = CustomHomePagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadOnlyRecipeSerializer
        return CreateUpdateRecipeSerializer

    @action(
        detail=True, methods=('post', 'delete',),
        permission_classes=(IsAuthenticated,),)
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return to_shopping_cart_or_favorite(
                request, recipe, ShoppingCartSerializer)

        if request.method == 'DELETE':
            return remove_from_shopping_cart_or_favorites(
                request, recipe, ShoppingCart)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,))
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
        detail=True, methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),)
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return to_shopping_cart_or_favorite(
                request, recipe, FavoriteRecipeSerializer)

        if request.method == 'DELETE':
            return remove_from_shopping_cart_or_favorites(
                request, recipe, FavoriteRecipe)

    @action(
        methods=('get',), detail=True,
        url_path='get-link', url_name='get-link',)
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        link = f'{RECIPE_LINK}/{recipe.id}/'
        return Response({'short-link': link}, status=status.HTTP_200_OK)
