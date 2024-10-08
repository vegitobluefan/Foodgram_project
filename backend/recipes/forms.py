from django import forms
from django.contrib.auth.forms import UserChangeForm

from .models import Recipe, User


class RecipeForm(forms.ModelForm):
    """Форма для модели Recipe."""

    class Meta:
        model = Recipe
        fields = (
            'author', 'name', 'image', 'text',
            'tags', 'ingredients', 'cooking_time',
        )


class UserForm(UserChangeForm):
    """Форма редактирования пользователя."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)
