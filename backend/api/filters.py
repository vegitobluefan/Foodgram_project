from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag
from rest_framework.filters import SearchFilter


class IngredientFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',)
    is_favorited = filters.NumberFilter(method='filter_favorited')
    is_in_shopping_cart = filters.NumberFilter(method='filter_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)

    def filter_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite_recipe__user=self.request.user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(cart_recipe__user=self.request.user)
        return queryset
