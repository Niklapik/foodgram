from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

NAME_MAX_LENGTH = 80
SLUG_MAX_LENGTH = 50
UNIT_MAX_LENGTH = 20


class Tag(models.Model):
    name = models.CharField(unique=True, blank=False, null=False,
                            max_length=NAME_MAX_LENGTH, verbose_name='Название тега')

    slug = models.SlugField(unique=True, blank=False, null=False,
                            max_length=SLUG_MAX_LENGTH, verbose_name='Идентификатор')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(blank=False, null=False,
                            max_length=NAME_MAX_LENGTH, verbose_name='Название ингредиента')

    measurement_unit = models.CharField(blank=False, null=False,
                                        max_length=UNIT_MAX_LENGTH, verbose_name='Название единицы измерения')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    author = models.ForeignKey(User, blank=False, null=False,
                               on_delete=models.CASCADE, related_name='recipes',
                               verbose_name='Автор рецепта', )

    name = models.CharField(blank=False, null=False,
                            max_length=NAME_MAX_LENGTH, verbose_name='Название рецепта')

    image = models.ImageField(blank=False, null=False,
                              verbose_name='Картинка', upload_to='recipe_pictures')

    text = models.TextField(blank=False, null=False, verbose_name='Описание рецепта')

    ingredients = models.ManyToManyField(Ingredient, blank=False, through='RecipeIngredient',
                                         related_name='recipes', verbose_name='Ингредиенты')

    tags = models.ManyToManyField(Tag, blank=False, related_name='recipes', verbose_name='Теги')

    cooking_time = models.PositiveIntegerField(blank=False, null=False,
                                               verbose_name='Время приготовления в мин.')

    def __str__(self):
        return f'{self.author}: {self.name}'

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient_recipes')
    amount = models.PositiveSmallIntegerField(verbose_name='Количество')
    unit = models.CharField(max_length=UNIT_MAX_LENGTH, verbose_name='Название единицы измерения')

    def __str__(self):
        return f'{self.quantity} {self.unit} {self.ingredient.title}'

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')

    def __str__(self):
        return f'{self.user.username} добавил в избранное {self.recipe.title}'

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_carts', verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='in_shopping_carts',
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
