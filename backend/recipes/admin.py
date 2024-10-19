from django.contrib import admin
from users.models import User

from .models import Ingredient, Recipe, Tag

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(User)
