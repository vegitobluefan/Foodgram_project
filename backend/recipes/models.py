from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from foodgram.settings import (INGREDIENT_NAME_LEN, MAX_EMAIL_LEN,
                               MAX_NAME_LEN, MAX_TAG_LEN, MAX_TEXT_LEN,
                               MEASURMENT_UNIT_LEN)


class User(AbstractUser):
    """Модель для описания пользователя."""

    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=MAX_EMAIL_LEN,
        help_text='Введите вашу электронную почту'
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=MAX_NAME_LEN,
        unique=True,
        validators=(UnicodeUsernameValidator(),),
        help_text='Введите никнейм',
    )
    first_name = models.CharField(
        max_length=MAX_NAME_LEN,
        verbose_name='Имя',
        help_text='Введите ваше имя',
    )
    last_name = models.CharField(
        max_length=MAX_NAME_LEN,
        verbose_name='Фамилия',
        help_text='Введите вашу фамилию',
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='avatars',
        help_text='Добавьте ваш аватар',
        blank=True,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

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
        related_name='subscribed_to',
        verbose_name='Автор',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='self_subscription_constraint'
            )]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f'{self.user.username} подписчик {self.author.username}.'


class Tag(models.Model):
    """Модель для описания тегов."""

    name = models.CharField(
        max_length=MAX_TAG_LEN,
        verbose_name='Название',
        unique=True
    )
    slug = models.SlugField(
        max_length=MAX_TAG_LEN,
        verbose_name='Слаг',
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'теги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов рецепта."""

    name = models.CharField(
        max_length=INGREDIENT_NAME_LEN,
        verbose_name='Название',
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=MEASURMENT_UNIT_LEN,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'ингридиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredients')]

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Модель для описания рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=MAX_NAME_LEN,
        verbose_name='Название',
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipe_images/',
        help_text='Добавьте изображение блюда',
        blank=True
    )
    text = models.TextField(
        max_length=MAX_TEXT_LEN,
        verbose_name='Описание',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги блюда',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
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


class IngredientRecipe(models.Model):
    """Модель для связи ингредиентов и рецептов."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        help_text='Укажите ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Укажите количество',
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'ингредиенты рецепта'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe',),
                name='ingredient_recipe',
            ),)

    def __str__(self) -> str:
        return f'{self.ingredient} ингредиент в {self.recipe}.'


class ShoppingCartFavoriteBasemodel(models.Model):
    """Базовая модель для корзины и избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_favorite_cart_recipe')]


class FavoriteRecipe(ShoppingCartFavoriteBasemodel):
    """Модель для добавления рецептов в избранное."""

    class Meta:
        default_related_name = 'favorite_recipe'
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'рецепты в избранном'

    def __str__(self) -> str:
        return f'{self.user} добавил {self.recipe} в избранное.'


class ShoppingCart(ShoppingCartFavoriteBasemodel):
    """Модель для добавления рецептов в корзину."""

    class Meta:
        default_related_name = 'cart_recipe'
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'рецепты в списке покупок'

    def __str__(self) -> str:
        return f'{self.user} добавил {self.recipe} в список покупок.'
