from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet

from recipes.models import Tag, Ingredient, FavoriteRecipe, Recipe, User
from users.models import Subscription

from .serializers import (TagSerializer, IngredientSerializer, RecipeSerializer,
                          SubscriptionSerializer, UserSerializer, FavoriteRecipeSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"error": "Рецепт уже в избранном"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            favorite_recipes = user.favorite_recipes.create(recipe=recipe)
            serializer = FavoriteRecipeSerializer(favorite_recipes)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


        elif request.method == 'DELETE':
            deleted, _ = FavoriteRecipe.objects.filter(user=user, recipe=recipe).delete()
            if not deleted:
                return Response(
                    {"error": "Рецепт не был в избранном"},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


# class CustomUserCreateViewSet(UserViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        serializer = SubscriptionSerializer(subscriptions, context={'request': request}, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)

        if author == user:
            return Response({'detail': 'Нельзя подписаться на самого себя.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            subscription, created = Subscription.objects.get_or_create(user=user, author=author)
            if not created:
                return Response({'detail': 'Вы уже подписаны на этого пользователя.'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionSerializer(subscription, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            deleted, _ = Subscription.objects.filter(user=user, author=author).delete()
            if deleted == 0:
                return Response({'detail': 'Вы не были подписаны на этого пользователя.'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)
