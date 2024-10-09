from recipes.models import Ingredient, Recipe, Tag, User
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',)


class NewUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Среиализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeSerializer(serializers.ModelSerializer):
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
