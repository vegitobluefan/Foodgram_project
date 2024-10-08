from recipes.views import Ingredient, Recipe, Tag
from rest_framework import serializers


class IngredientSerializer(serializers.Serializer):
    """Среиализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeSerializer(serializers.Serializer):
    """Сериализатор для модели Recipe."""

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text', 'tags',
            'ingredients', 'cooking_time', 'pub_date',
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)
