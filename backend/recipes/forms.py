from django import forms
from django.contrib.auth.forms import UserChangeForm

from .models import Recipe, User


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = ('__all__')


class UserForm(UserChangeForm):
    """User editing form."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)
