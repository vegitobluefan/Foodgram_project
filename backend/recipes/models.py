from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель для описания тегов."""

    name = models.CharField(
        max_length=32, verbose_name='Название', unique=True
    )
    slug = models.SlugField(max_length=32, verbose_name='Слаг', unique=True,)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'теги'

    def __str__(self) -> str:
        return self.title


class Ingredient(models.Model):
    """Модель продуктов для приготовления блюда по рецепту."""

    name = models.CharField(
        max_length=32, verbose_name='Название', unique=True
    )
    measurement_unit = models.CharField(
        max_length=12, verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'ингридиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.title


class Recipe(models.Model):
    """Модель для описания рецептов."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=32, verbose_name='Название'
    )
    image = models.ImageField(
        verbose_name='Изображение', upload_to='recipe_images/',
    )
    text = models.TextField(
        max_length=256, verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient, related_name='recipe', verbose_name='Ингредиенты блюда'
    )
    tags = models.ManyToManyField(
        Tag, related_name='recipe', verbose_name='Теги блюда',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (мин.)', default=0,
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
        return self.title
