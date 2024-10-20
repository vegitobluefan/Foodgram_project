from django.contrib import admin

from users.models import MyUser

from .models import Ingredient, Recipe, Tag

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(MyUser)
