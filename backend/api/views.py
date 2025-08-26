from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.request import Request
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription
from .filters import IngredientFilter, RecipeFilter
from .paginators import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer, FavoriteRecipeSerializer, IngredientSerializer, PostFavoriteRecipeSerializer,
    RecipePostSerializer, RecipeSerializer, ShoppingCartSerializer,
    SubscriptionSerializer, TagSerializer, UserSerializer
)
from .utils import create_shopping_list
from django.contrib.auth import get_user_model

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipePostSerializer
        return RecipeSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        queryset = queryset.select_related('author')
        queryset = queryset.prefetch_related('tags', 'ingredients')
        return queryset

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            serializer = FavoriteRecipeSerializer(
                data={'recipe': recipe.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)

            recipe_serializer = PostFavoriteRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(recipe_serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if not FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепта не было в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = ShoppingCartSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            deleted, _ = ShoppingCart.objects.filter(
                user=user,
                recipe=recipe
            ).delete()
            if not deleted:
                return Response(
                    {'errors': 'Рецепта не было в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        recipes = [item.recipe for item in shopping_cart]
        return create_shopping_list(recipes)

    @action(detail=True, methods=('GET',), url_path='get-link')
    def get_short_link(self, request: Request, pk: int):
        try:
            recipe: Recipe = self.get_object()
        except Recipe.DoesNotExist:
            return Response(
                {'message': 'Не существует такой записи'},
                status=status.HTTP_404_NOT_FOUND
            )

        scheme = request.scheme
        host = request.get_host()
        domain = f'{scheme}://{host}'
        return Response(
            {'short-link': f'{domain}/recipes/{recipe.id}'},
            status=status.HTTP_200_OK
        )


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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    @action(detail=False, methods=('get',), url_path='subscriptions')
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        page = self.paginate_queryset(subscriptions)

        if page is not None:
            serializer = SubscriptionSerializer(page, many=True,
                                                context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionSerializer(subscriptions, many=True,
                                            context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=('post', 'delete'), url_path='subscribe')
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(self.queryset, pk=id)

        if author == user:
            return Response(
                {'detail': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            subscription, created = Subscription.objects.get_or_create(
                user=user,
                author=author
            )
            if not created:
                return Response(
                    {'detail': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscriptionSerializer(subscription,
                                                context={'request': request})
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

    @action(detail=False, methods=('put', 'delete'), url_path='me/avatar')
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            if not user.avatar:
                return Response({"error": "Аватар не установлен"},
                                status=status.HTTP_400_BAD_REQUEST)

            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
