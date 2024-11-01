from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, MyUser, Recipe, ShoppingCart,
                     SubscriptionUser, Tag)

admin.site.register(MyUser)
admin.site.register(SubscriptionUser)
admin.site.register(FavoriteRecipe)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
