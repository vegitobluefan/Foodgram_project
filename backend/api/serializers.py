from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from foodgram.settings import MAX_VALUE_VALIDATOR, MIN_VALUE_VALIDATOR
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            MyUser, Recipe, ShoppingCart, SubscriptionUser,
                            Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватаров."""

    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = MyUser
        fields = ('avatar',)


class RecipeShortInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для краткой информации о рецептах."""

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


class UserGetSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения подписок пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = (
            'id', 'is_subscribed', 'recipes', 'recipes_count',
            'email', 'username', 'first_name', 'last_name',
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name',)

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
        serializer = ReadOnlyRecipeSerializer(
            recipes, context={"request": request}, many=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class UserPostDelSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для удаления и создания подписки пользователя."""

    class Meta:
        model = SubscriptionUser
        fields = ('author', 'user',)

    def validate(self, data):
        if data.get('author') == data.get('user'):
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')
        if SubscriptionUser.objects.filter(
            author=data.get('author'),
            user=data.get('user')
        ).exists():
            raise serializers.ValidationError('Подписка уже существует.')
        return data

    def to_representation(self, instance):
        return UserGetSubscribeSerializer(
            instance=instance.user,
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
        validators=[
            UniqueValidator(
                queryset=Tag.objects.all(), message='Такой тег уже существует!'
            )],)
    slug = serializers.SlugField(
        validators=[
            UniqueValidator(
                queryset=Tag.objects.all(),
                message='Такой слаг тега уже существует!')],)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели IngredientRecipe."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

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
                MIN_VALUE_VALIDATOR, 'Должен быть хотя бы один ингредиент.'
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
            request and request.user.is_authenticated
            and FavoriteRecipe.objects.filter(
                user=request.user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user, recipe=obj).exists())


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования своих рецептов."""

    author = UserSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(MIN_VALUE_VALIDATOR),
            MaxValueValidator(MAX_VALUE_VALIDATOR)
        ),
        error_messages={'validators': 'Неподходящее время приготовления'})

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags',
            'image', 'name', 'text', 'cooking_time',)

    @staticmethod
    def add_ingredients(recipe, tags, ingredients):
        recipe.tags.set(tags)
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient.get('id')),
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        with transaction.atomic():
            recipe = Recipe.objects.create(
                author=self.context['request'].user, **validated_data
            )
            self.add_ingredients(recipe, tags, ingredients)
            return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        IngredientRecipe.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        self.add_ingredients(instance, tags, ingredients)
        instance.save()
        return instance

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
