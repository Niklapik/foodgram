from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

TITLE_MAX_LENGTH = 40
SLUG_MAX_LENGTH = 50
UNIT_MAX_LENGTH = 20


class Tag(models.Model):
    title = models.CharField(unique=True, blank=False, null=False,
                             max_length=TITLE_MAX_LENGTH, verbose_name='Название тега')

    slug = models.SlugField(unique=True, blank=False, null=False,
                            max_length=SLUG_MAX_LENGTH, verbose_name='Идентификатор')

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    title = models.CharField(blank=False, null=False,
                             max_length=TITLE_MAX_LENGTH, verbose_name='Название ингредиента')

    unit = models.CharField(blank=False, null=False,
                            max_length=UNIT_MAX_LENGTH, verbose_name='Название единицы измерения')

    def __str__(self):
        return self.title


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               blank=False, null=False,
                               verbose_name='Автор рецепта', related_name='recipes')

    title = models.CharField(blank=False, null=False,
                             max_length=TITLE_MAX_LENGTH, verbose_name='Название рецепта')

    image = models.ImageField('Картинка', upload_to='recipe_pictures', blank=False)

    description = models.TextField(verbose_name='Описание рецепта')

    cooking_time = models.PositiveIntegerField(blank=False, null=False,
                                               verbose_name='Время приготовления в мин.')
