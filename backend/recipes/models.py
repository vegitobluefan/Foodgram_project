from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    """Модель для описания пользователя."""

    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=256,
        help_text='Введите вашу электронную почту'
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=32,
        unique=True,
        validators=(validate_username, UnicodeUsernameValidator(),),
        help_text='Введите никнейм',
    )
    first_name = models.CharField(
        max_length=32,
        verbose_name='Имя',
        help_text='Введите ваше имя',
    )
    last_name = models.CharField(
        max_length=32,
        verbose_name='Фамилия',
        help_text='Введите вашу фамилию',
    )

    class Meta(AbstractUser.Meta):
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Tag(models.Model):
    """Модель для описания тегов."""

    name = models.CharField(
        max_length=32,
        verbose_name='Название',
        unique=True
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name='Слаг',
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'теги'

    def __str__(self) -> str:
        return self.title


class Ingredient(models.Model):
    """Модель продуктов для приготовления блюда по рецепту."""

    name = models.CharField(
        max_length=32,
        verbose_name='Название',
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=12,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'ингридиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Модель для описания рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        # related_name='recipes',
    )
    name = models.CharField(
        max_length=32,
        verbose_name='Название'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipe_images/',
    )
    text = models.TextField(
        max_length=256,
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты блюда'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги блюда',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (мин.)',
        validators=(
            MinValueValidator(0),
            MaxValueValidator(10000)
        ),
        error_messages={'validators': 'Неподходящее время приготовления'}
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.name
