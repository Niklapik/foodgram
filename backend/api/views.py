from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions

from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet

from recipes.models import Tag, Ingredient, FavoriteRecipe, Recipe, User
from users.models import Subscription

from .serializers import (TagSerializer, IngredientSerializer, RecipeSerializer, RecipePostSerializer,
                          SubscriptionSerializer, UserSerializer, UserCreateSerializer,
                          AvatarSerializer, PostFavoriteRecipeSerializer)

from .permissions import IsAdminOrReadOnly

from rest_framework.permissions import (
    AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipePostSerializer
        return RecipeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('author')
        queryset = queryset.prefetch_related('tags', 'ingredients')
        return queryset

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            serializer = PostFavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            deleted, _ = FavoriteRecipe.objects.filter(user=user, recipe=recipe).delete()
            if deleted == 0:
                return Response(
                    {'errors': 'Рецепта не было в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    permission_classes = (AllowAny,)


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        page = self.paginate_queryset(subscriptions)

        if page is not None:
            serializer = SubscriptionSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionSerializer(subscriptions, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(self.queryset, pk=id)

        if author == user:
            return Response(
                {'detail': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            subscription, created = Subscription.objects.get_or_create(user=user, author=author)
            if not created:
                return Response({'detail': 'Вы уже подписаны на этого пользователя.'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
            serializer = SubscriptionSerializer(subscription, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            deleted, _ = Subscription.objects.filter(
                user=user,
                author=author
            ).delete()
            if not deleted:
                return Response(
                    {'detail': 'Вы не были подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            if not user.avatar:
                return Response({"error": "Аватар не установлен"}, status=status.HTTP_400_BAD_REQUEST)

            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
