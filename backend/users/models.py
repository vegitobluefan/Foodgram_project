from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    """Модель для описания пользователя."""

    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=254,
        help_text='Введите вашу электронную почту'
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
        validators=(validate_username, UnicodeUsernameValidator(),),
        help_text='Введите никнейм',
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        help_text='Введите ваше имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        help_text='Введите вашу фамилию',
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='user_avatars',
        help_text='Добавьте ваш аватар',
        blank=True,
    )

    class Meta(AbstractUser.Meta):
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class SubscriptionUser(models.Model):
    """Модель подписки пользователей."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор',
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f'{self.subscriber.username} подписчик {self.author.username}.'
