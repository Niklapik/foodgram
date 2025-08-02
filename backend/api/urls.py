from rest_framework.routers import SimpleRouter

from django.urls import include, path

from .views import TagViewSet, IngredientViewSet, RecipeViewSet, UserViewSet

router = SimpleRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
# router.register(rf"recipes/(?P<id>[1-9]\d*)/favorite", FavoriteRecipeViewSet, basename="favorite")
router.register('users', UserViewSet, basename='users')

# urlpatterns = [
#     path('', include(router.urls)),
#     path('', include('djoser.urls')),
#     path('', include('djoser.urls.jwt')),
# ]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
