from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet, get_token,
                    registration)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('/auth/signup/', registration),
    path('/auth/token/', get_token),
    # path('', include('djoser.urls')),
    # path('auth/', include('djoser.urls.authtoken')),
]
