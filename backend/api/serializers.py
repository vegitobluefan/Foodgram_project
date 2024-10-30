from django.core.validators import MaxValueValidator, MinValueValidator
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.serializers import UserSerializer

from .utils import Base64ImageField


class IngredientSerializer(serializers.ModelSerializer):
    """Среиализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    name = serializers.CharField(
        max_length=32,
        validators=[
            UniqueValidator(
                queryset=Tag.objects.all(), message='Такой тег уже существует!'
            )],
    )
    slug = serializers.SlugField(
        max_length=32,
        validators=[
            UniqueValidator(
                queryset=Tag.objects.all(),
                message='Такой слаг тега уже существует!')],
    )

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели IngredientRecipe."""

    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()
    amount = serializers.ReadOnlyField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор работы со связью рецептов и ингредиентов."""

    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(
        required=True,
        validators=[
            MinValueValidator(
                1, 'Должен быть хотя бы один ингредиент.'
            )]
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount',)


class ReadOnlyRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    author = UserSerializer(read_only=True,)
    image = Base64ImageField()
    tags = TagSerializer(
        many=True, read_only=True,
    )
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='recipeingredient',
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text', 'tags', 'ingredients',
            'pub_date', 'cooking_time', 'is_favorited',
            'is_in_shopping_cart',)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and obj.favorite_recipe.filter(user=request.user).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and obj.cart_recipe.filter(user=request.user).exists())


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования своих рецептов."""

    ingredients = AddIngredientToRecipeSerializer(
        many=True,
        source='recipeingredient',
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10000)
        ),
        error_messages={'validators': 'Неподходящее время приготовления'}
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',)

    def add_ingredients(self, ingredients, recipe):
        ingredient_list = [
            IngredientRecipe(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient.get('id')),
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        ]
        IngredientRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('recipeingredient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipeingredient')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        IngredientRecipe.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        self.add_ingredients(ingredients, instance)
        instance.save()
        return instance

    def validate_image(self, image_data):
        if image_data is None:
            raise serializers.ValidationError(
                'Добавьте изображение рецепта.'
            )
        return image_data

    def to_representation(self, instance):
        serializer = ReadOnlyRecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов"""

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe',)


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)
