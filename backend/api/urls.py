from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import MyUserViewSet, UserSubscriptionsViewSet

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('users', MyUserViewSet, basename='users')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        "users/subscriptions/",
        UserSubscriptionsViewSet.as_view({"get": "list"}),
    ),
    path('', include(router_v1.urls)),
]
