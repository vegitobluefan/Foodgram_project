from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, validators

from .models import SubscriptionUser, User, models


class MyUserSerializer(UserSerializer):
    """Сериализатор для пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'avatar',
            'first_name', 'last_name', 'is_subscribed',
        )
        read_only_fields = ('avatar', 'is_subscribed',)

    def get_subscription(self, obj):
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
                queryset=User.objects.all(),
                message='Пользователь с таким никнеймом уже существует!'
            )
        ]
    )
    email = models.EmailField(
        validators=[
            validators.UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с такой почтой уже существует!'
            )
        ]
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password',
        )


class UserAccessTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(required=True, max_length=52)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        if not default_token_generator.check_token(
            user, data['confirmation_code']
        ):
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения'})
        return data
