from django import forms
from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework.authtoken.models import TokenProxy

from api.constants import RECIPE_NO_INGREDIENTS_MESSAGE

from .models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = ('author', 'name',)
    list_editable = ('name',)
    search_fields = ('author__username', 'name',)
    list_filter = ('tags',)

    def response_add(self, request, obj, post_url_continue=None):
        if not obj.ingredients.exists():
            obj.delete()
            messages.error(request, RECIPE_NO_INGREDIENTS_MESSAGE)
            return HttpResponseRedirect(reverse('admin:recipes_recipe_add'))
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if not obj.ingredients.exists():
            messages.error(request, RECIPE_NO_INGREDIENTS_MESSAGE)
            return HttpResponseRedirect(reverse(
                'admin:recipes_recipe_change',
                args=[obj.pk]))
        return super().response_change(request, obj)


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
