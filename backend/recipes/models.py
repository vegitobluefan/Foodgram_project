from django.db import models
from users.models import MyUser


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
        return self.name


class Ingredient(models.Model):
    """Модель продуктов для приготовления блюда по рецепту."""

    name = models.CharField(
        max_length=128,
        verbose_name='Название',
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=64,
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
        MyUser,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipe_images/',
        help_text='Добавьте изображение блюда',
        blank=True
    )
    text = models.TextField(
        max_length=512,
        verbose_name='Описание',
    )
    ingredient = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты блюда',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
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
        related_name='recipeingredient',
        verbose_name='Ингредиент',
        help_text='Укажите ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredient',
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


class TagRecipe(models.Model):
    """Модель для связи тегов и рецептов."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tagrecipe',
        verbose_name='Тег',
        help_text='Выберите тег(и)',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tagrecipe',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'теги рецепта'

    def __str__(self) -> str:
        return f'{self.tag} - тег для {self.recipe}.'


class FavoriteRecipe(models.Model):
    """Модель для добавления рецептов в избранное."""

    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт в избранное',
    )

    class Meta:
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'рецепты в избранном'

    def __str__(self) -> str:
        return f'{self.user} добавил {self.recipe} в избранное.'


class ShoppingCart(models.Model):
    """Модель для добавления рецептов в корзину."""

    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='cart_recipe',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart_recipe',
        verbose_name='Рецепт в корзину',
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'рецепты в списке покупок'

    def __str__(self) -> str:
        return f'{self.user} добавил {self.recipe} в список покупок.'
