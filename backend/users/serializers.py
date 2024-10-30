from api.utils import Base64ImageField
from djoser.serializers import UserCreateSerializer
from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import MyUser, SubscriptionUser, models


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
                message='Пользователь с таким никнеймом уже существует!'
            )
        ]
    )
    email = models.EmailField(
        validators=[
            UniqueValidator(
                queryset=MyUser.objects.all(),
                message='Пользователь с такой почтой уже существует!'
            )
        ]
    )

    class Meta:
        model = MyUser
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password',
        )


class UserGetSubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = ('id', 'is_subscribed', 'recipes', 'recipes_count',
                  'email', 'id', 'username', 'first_name', 'last_name',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return SubscriptionUser.objects.filter(
            user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.POST.get('recipes_limit')
        queryset = obj.recipes.all()
        if recipes_limit:
            queryset = queryset[:(recipes_limit)]
        return RecipeShortInfoSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()


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
