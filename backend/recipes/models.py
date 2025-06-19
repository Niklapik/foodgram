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
