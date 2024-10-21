import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import MyUser, SubscriptionUser, models


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class MyUserSerializer(UserSerializer):
    """Сериализатор для пользователя."""

    avatar = Base64ImageField(required=False, allow_null=True)
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

    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None


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
