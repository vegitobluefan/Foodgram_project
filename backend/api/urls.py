from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AuthView, IngredientViewSet, RecipeViewSet, TagViewSet,
                    UserViewSet)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router_v1.urls)),
    # path('auth/signup/', registration),
    path('auth/token/login', AuthView.as_view(), name='token'),
    # path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
