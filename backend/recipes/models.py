from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

NAME_MAX_LENGTH = 40
SLUG_MAX_LENGTH = 50
UNIT_MAX_LENGTH = 20


class Tag(models.Model):
    name = models.CharField(unique=True, blank=False, null=False,
                            max_length=NAME_MAX_LENGTH, verbose_name='Название тега')

    slug = models.SlugField(unique=True, blank=False, null=False,
                            max_length=SLUG_MAX_LENGTH, verbose_name='Идентификатор')

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    name = models.CharField(blank=False, null=False,
                            max_length=NAME_MAX_LENGTH, verbose_name='Название ингредиента')

    measurement_unit = models.CharField(blank=False, null=False,
                                        max_length=UNIT_MAX_LENGTH, verbose_name='Название единицы измерения')

    def __str__(self):
        return self.title


class Recipe(models.Model):
    # blank=False, null=False
    author = models.ForeignKey(User, blank=True, null=True,
                               on_delete=models.CASCADE, related_name='recipes',
                               verbose_name='Автор рецепта', )

    name = models.CharField(blank=False, null=False,
                            max_length=NAME_MAX_LENGTH, verbose_name='Название рецепта')

    # blank=False, null=False
    image = models.ImageField(blank=True,
                              verbose_name='Картинка', upload_to='recipe_pictures')

    text = models.TextField(blank=False, null=False, verbose_name='Описание рецепта')

    # blank=False
    ingredients = models.ManyToManyField(Ingredient, blank=True, through='RecipeIngredient',
                                         related_name='recipes', verbose_name='Ингредиенты')

    # blank=False
    tags = models.ManyToManyField(Tag, blank=True, related_name='recipes', verbose_name='Теги')

    cooking_time = models.PositiveIntegerField(blank=False, null=False,
                                               verbose_name='Время приготовления в мин.')


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient_recipes')
    quantity = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Количество')
    unit = models.CharField(max_length=UNIT_MAX_LENGTH, verbose_name='Название единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f'{self.quantity} {self.unit} {self.ingredient.title}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user.username} добавил в избранное {self.recipe.title}'
