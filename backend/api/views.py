from django.db.models import Sum
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from foodgram.settings import RECIPE_LINK
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            MyUser, Recipe, ShoppingCart, SubscriptionUser,
                            Tag)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .paginators import CustomHomePagination
from .serializers import (AvatarSerializer, CreateUpdateRecipeSerializer,
                          FavoriteRecipeSerializer, IngredientSerializer,
                          ReadOnlyRecipeSerializer, ShoppingCartSerializer,
                          TagSerializer, UserGetSubscribeSerializer,
                          UserSerializer)
from .utils import delete_method, download_cart, post_method


class MyUserViewSet(UserViewSet):
    """Вьюсет для модели User."""

    serializer_class = UserSerializer
    queryset = MyUser.objects.all()
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
        detail=False, methods=('get'), permission_classes=(IsAuthenticated,),)
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=True, methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),)
    def subscribe(self, request, id=None):
        subscriber = self.request.user
        author = get_object_or_404(MyUser, pk=id)

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


class UserSubscriptionsViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet
):
    """Viewset для отображения подписок пользователя."""
    serializer_class = UserGetSubscribeSerializer

    def get_queryset(self):
        return MyUser.objects.filter(author__user=self.request.user)


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
            return post_method(request, recipe, ShoppingCartSerializer)

        if request.method == 'DELETE':
            return delete_method(request, recipe, ShoppingCart)
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
        detail=True, methods=('post',), permission_classes=(IsAuthenticated,),)
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
        methods=('get',), detail=True,
        url_path='get-link', url_name='get-link',)
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        link = f'{RECIPE_LINK}/{recipe.id}/'
        return Response({'short-link': link}, status=status.HTTP_200_OK)
