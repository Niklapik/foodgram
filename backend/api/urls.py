from rest_framework.routers import SimpleRouter

from django.urls import include, path

from .views import TagViewSet, IngredientViewSet, FavoriteRecipeViewSet, RecipeViewSet

router = SimpleRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(rf"recipes/(?P<id>[1-9]\d*)/favorite", FavoriteRecipeViewSet, basename="favorite")

urlpatterns = [
    path('', include(router.urls)),
]
