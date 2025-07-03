from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

from django.urls import include, path

from .views import TagViewSet, IngredientViewSet, RecipeViewSet, SubscriptionViewSet

router = SimpleRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
# router.register(rf"recipes/(?P<id>[1-9]\d*)/favorite", FavoriteRecipeViewSet, basename="favorite")
router.register('users', SubscriptionViewSet, basename='users')

# urlpatterns = [
#     path('', include(router.urls)),
#     path('', include('djoser.urls')),
#     path('', include('djoser.urls.jwt')),
# ]

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/token/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
]
