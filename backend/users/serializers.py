from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, validators

from .models import SubscriptionUser, MyUser, models


class MyUserSerializer(UserSerializer):
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
        return (
            request.user.is_authenticated
            and SubscriptionUser.objects.filter(
                user=request.user, author=obj
            ).exists()
        )


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
