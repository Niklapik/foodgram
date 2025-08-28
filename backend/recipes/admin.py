from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import FavoriteRecipe, Ingredient, Recipe, ShoppingCart, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name',)
    list_editable = ('name',)
    search_fields = ('author', 'name',)
    list_filter = ('tags',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    list_editable = ('slug',)
    search_fields = ('name', 'slug',)
    list_filter = ('name', 'slug',)


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    list_editable = ('recipe',)
    search_fields = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    list_editable = ('recipe',)
    search_fields = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
