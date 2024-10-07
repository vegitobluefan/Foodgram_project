from django.urls import include, path
from foodgram.urls import API_VERSION
from rest_framework.routers import SimpleRouter

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet, get_token,
                    registration)

router_v1 = SimpleRouter()
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path(f'{API_VERSION}/', include(router_v1.urls)),
    path(f'{API_VERSION}/auth/signup/', registration),
    path(f'{API_VERSION}/auth/token/', get_token),
]
