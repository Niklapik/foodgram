from django_filters import rest_framework as filters
from django.db.models import Exists, OuterRef
from recipes.models import Recipe, FavoriteRecipe, ShoppingCart, Ingredient
from django.db.models import Q


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name='author__id')
    tags = filters.CharFilter(method='filter_tags')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_tags(self, queryset, name, value):
        tag_slugs = self.request.GET.getlist('tags')
        return queryset.filter(tags__slug__in=tag_slugs).distinct() if tag_slugs else queryset

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if value else queryset
        favorite_subquery = FavoriteRecipe.objects.filter(
            user=user,
            recipe=OuterRef('pk')
        )
        return queryset.annotate(
            is_favorite=Exists(favorite_subquery)
        ).filter(is_favorite=value)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if value else queryset
        cart_subquery = ShoppingCart.objects.filter(
            user=user,
            recipe=OuterRef('pk')
        )
        return queryset.annotate(
            in_cart=Exists(cart_subquery)
        ).filter(in_cart=value)
