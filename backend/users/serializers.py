from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, validators
from api.serializers import Base64ImageField

from .models import MyUser, SubscriptionUser, models


class MyUserSerializer(UserSerializer):
    """Сериализатор для пользователя."""

    image = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed',
    )
    image_url = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )

    class Meta:
        model = MyUser
        fields = (
            'id', 'email', 'username', 'avatar',
            'first_name', 'last_name', 'is_subscribed',
        )
        read_only_fields = ('avatar', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and SubscriptionUser.objects.filter(
                user=request.user, author=obj
            ).exists()
        )

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class MyUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    username = models.CharField(
        validators=[
            validators.UniqueValidator(
                queryset=MyUser.objects.all(),
                message='Пользователь с таким никнеймом уже существует!'
            )
        ]
    )
    email = models.EmailField(
        validators=[
            validators.UniqueValidator(
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
