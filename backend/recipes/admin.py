from django.contrib import admin
from users.models import MyUser, SubscriptionUser

from .models import FavoriteRecipe, Ingredient, Recipe, ShoppingCart, Tag

admin.site.register(MyUser)
admin.site.register(SubscriptionUser)
admin.site.register(FavoriteRecipe)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
