from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from users.models import MyUser, SubscriptionUser, models

from .utils import Base64ImageField


class AvatarSerializer(serializers.ModelSerializer):
    """Сериалтзатор для аватаров."""

    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = MyUser
        fields = ('avatar',)


class RecipeShortInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = (
            'id', 'email', 'username', 'avatar',
            'first_name', 'last_name', 'is_subscribed',
        )
        read_only_fields = ('avatar', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        user = request.user
        return user.is_authenticated and SubscriptionUser.objects.filter(
            user=user, author=obj
        ).exists()


class MyUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    username = models.CharField(
        validators=[
            UniqueValidator(
                queryset=MyUser.objects.all(),
                message='Пользователь с таким никнеймом уже существует!')])
    email = models.EmailField(
        validators=[
            UniqueValidator(
                queryset=MyUser.objects.all(),
                message='Пользователь с такой почтой уже существует!')])

    class Meta:
        model = MyUser
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password',)


class UserGetSubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = (
            'id', 'is_subscribed', 'recipes', 'recipes_count',
            'email', 'username', 'first_name', 'last_name',
        )
        read_only_fields = ('email', 'first_name', 'last_name', 'username',)

    def validate(self, data):
        request = self.context.get('request')
        author_id = request.parser_context.get('kwargs').get('id')
        author = get_object_or_404(MyUser, id=author_id)
        user = request.user
        if user.subscriber.filter(author=author_id).exists():
            raise ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return SubscriptionUser.objects.filter(
            user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj)
        if limit:
            recipes = recipes[:int(limit)]
        serializer = ReadOnlyRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class UserPostDelSubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubscriptionUser
        fields = ('subscribing_to', 'subscriber',)

    def validate(self, data):
        if data.get('subscribing_to') == data.get('subscriber'):
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )

        if SubscriptionUser.objects.filter(
            subscribing_to=data.get('subscribing_to'),
            subscriber=data.get('subscriber')
        ).exists():
            raise serializers.ValidationError('Подписка уже существует.')
        return data

    def to_representation(self, instance):
        return UserGetSubscribeSerializer(
            instance=instance.subscriber,
            context={'request': self.context.get('request')}
        ).data


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
        ingredients = validated_data.pop('recipeingredient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
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
