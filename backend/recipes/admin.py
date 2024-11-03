from django.contrib import admin
from django.utils.html import format_html

from .models import (FavoriteRecipe, Ingredient, MyUser, Recipe, ShoppingCart,
                     SubscriptionUser, Tag)

admin.site.register(MyUser)
admin.site.register(SubscriptionUser)
admin.site.register(FavoriteRecipe)
admin.site.register(Ingredient)
admin.site.register(ShoppingCart)
admin.site.register(Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'recipe_favorite',)

    @admin.display(
        description=format_html('<strong>Рецепт в избранных</strong>'))
    def recipe_favorite(self, Recipe):
        return Recipe.favorite_recipe.count()
# Данные от админки:
# Логин: daniyar
# Пароль: arinov1701
