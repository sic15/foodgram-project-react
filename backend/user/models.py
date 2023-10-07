from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from core import constants as c


class User(AbstractUser):
    username = models.CharField(
        max_length=c.MAX_USER_FIELD_LENGTH,
        verbose_name='Username',
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Имя пользователя содержит недопустимый символ'
        )]
    )
    email = models.EmailField(
        max_length=c.MAX_USER_FIELD_LENGTH,
        unique=True,
        verbose_name='email',
    )
    first_name = models.CharField(
        max_length=c.MAX_USER_FIELD_LENGTH,
        verbose_name='имя',
        blank=True
    )
    last_name = models.CharField(
        max_length=c.MAX_USER_FIELD_LENGTH,
        verbose_name='фамилия',
        blank=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Подписан на:'
    )

    def __str__(self):
        return (f'Пользователь {self.user.username}'
                f'подписан на {self.author.username}')

    class Meta:
        verbose_name = 'Подписка на авторов'
        verbose_name_plural = 'Подписки на авторов'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe'
            )
        ]
