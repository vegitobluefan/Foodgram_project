from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe, Tag
from rest_framework.filters import SearchFilter


class IngredientFilter(SearchFilter):
    """Фильтрация ингредиентов по названию при поиске."""

    search_param = 'name'


class RecipeFilter(FilterSet):
    """Фильтрация рецептов по наличию в корзине и избранном."""

    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',)
    is_favorited = filters.NumberFilter(method='filter_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_shopping_cart')
    is_subscribed = filters.BooleanFilter(method='filter_subscription')

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

    def filter_subscription(self, queryset, name, value):
        return queryset.filter(author=self.request.filter)
