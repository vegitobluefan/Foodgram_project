from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from rest_framework.authtoken.models import TokenProxy

from foodgram.settings import ONE_NUM, ZERO_NUM

from .models import (FavoriteRecipe, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, SubscriptionUser, Tag, TagRecipe, User)

admin.site.register(SubscriptionUser)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
admin.site.unregister([Group, TokenProxy])


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ('email', 'username')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)


class RecipeTagIngredientAdmin(admin.TabularInline):
    min_num = ONE_NUM
    extra = ZERO_NUM


class RecipeIngredientInline(RecipeTagIngredientAdmin):
    model = IngredientRecipe


class RecipeTagInline(admin.TabularInline):
    model = TagRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    inlines = (RecipeIngredientInline, RecipeTagInline,)
    list_display = ('name', 'author', 'recipe_favorite',)
    list_filter = ('tags',)
    search_fields = ('name', 'author__username',)

    @admin.display(
        description=format_html('<strong>Рецепт в избранных</strong>'))
    def recipe_favorite(self, Recipe):
        return Recipe.favorite_recipe.count()
