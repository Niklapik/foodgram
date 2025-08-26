from django.contrib.auth.models import AbstractUser
from django.db import models

from api.constants import NAME_MAX_LENGTH


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=NAME_MAX_LENGTH, blank=False)
    last_name = models.CharField(max_length=NAME_MAX_LENGTH, blank=False)
    avatar = models.ImageField(upload_to='foodgram/images/',
                               null=True, default=None)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    def __str__(self):
        return self.email


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
