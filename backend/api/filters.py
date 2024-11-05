from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import MyUser, Recipe, Tag


class IngredientFilter(SearchFilter):
    """Фильтрация ингредиентов по названию при поиске."""

    search_param = 'name'


class RecipeFilter(FilterSet):
    """Фильтрация рецептов по наличию в корзине и избранном."""

    author = filters.ModelChoiceFilter(queryset=MyUser.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',)
    is_favorited = filters.BooleanFilter(method='filter_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart',)

    def filter_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite_recipe__user=self.request.user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(cart_recipe__user=self.request.user)
        return queryset
