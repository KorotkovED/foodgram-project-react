from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientsViewSet, RecipeViewSet, TagsViewSet

app_name = 'recipe'

router_v1 = DefaultRouter()
router_v1.register(r'tags', TagsViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientsViewSet,
                   basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet,
                   basename='recipes')

urlpatterns = [
    path(r'', include(router_v1.urls)),
]
