from django.contrib.auth import get_user_model
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models

from api.constants import (
    LIMIT_COOKING_MESSAGE,
    LIMIT_COOKING_TIME,
    LIMIT_INGREDIENTS,
    LIMIT_INGREDIENTS_MESSAGE,
    NAME_MAX_LENGTH,
    SLUG_MAX_LENGTH,
    UNIT_MAX_LENGTH,
)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(unique=True,
                            max_length=NAME_MAX_LENGTH,
                            verbose_name='Название тега')

    slug = models.SlugField(unique=True,
                            max_length=SLUG_MAX_LENGTH,
                            verbose_name='Идентификатор')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH,
                            verbose_name='Название ингредиента')

    measurement_unit = models.CharField(
        max_length=UNIT_MAX_LENGTH,
        verbose_name='Название единицы измерения')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор рецепта', )

    name = models.CharField(max_length=NAME_MAX_LENGTH,
                            verbose_name='Название рецепта')

    image = models.ImageField(verbose_name='Картинка',
                              upload_to='recipe_pictures')

    text = models.TextField(verbose_name='Описание рецепта')

    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         related_name='recipes',
                                         verbose_name='Ингредиенты')

    tags = models.ManyToManyField(Tag, related_name='recipes',
                                  verbose_name='Теги')

    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в мин.',
        validators=[validators.MinValueValidator(
            LIMIT_COOKING_TIME,
            message=LIMIT_COOKING_MESSAGE)])
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    def __str__(self):
        return f'{self.author}: {self.name}'

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created_at']


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredient_recipes')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[validators.MinValueValidator(
            LIMIT_INGREDIENTS,
            message=LIMIT_INGREDIENTS_MESSAGE)])
    unit = models.CharField(max_length=UNIT_MAX_LENGTH,
                            verbose_name='Название единицы измерения')

    def clean(self):
        super().clean()
        if self.pk and not self.recipe_ingredients.exists():
            raise ValidationError('Добавьте хотя бы один ингредиент')

    def __str__(self):
        return f'{self.quantity} {self.unit} {self.ingredient.title}'

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorited_by')

    def __str__(self):
        return f'{self.user.username} добавил в избранное {self.recipe.title}'

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='shopping_carts',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='in_shopping_carts',
                               verbose_name='Рецепт')

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
