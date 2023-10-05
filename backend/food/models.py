from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify
from transliterate import translit

from user.models import User


class Tag(models.Model):
    name = models.CharField(max_length=20, verbose_name='Имя тэга')
    color = models.CharField(max_length=7, verbose_name='Цвет')
    slug = models.SlugField(default='', null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(translit(self.name, 'ru', reversed=True))
        super(Tag, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    MEASURE_CHOISES = [('g', 'г'), ('kg', 'кг'), ('l', 'л'),
                       ('ml', 'мл'), ('piece', 'шт')]

    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=10, choices=MEASURE_CHOISES)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Игредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes')
    name = models.CharField(max_length=50)
    text = models.TextField()
    cooking_time = models.IntegerField()
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='AmountIngredient')
    tags = models.ManyToManyField(Tag, related_name='recipe')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class AmountIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество", validators=(
            MinValueValidator(
                0, "Количество не может быть 0"),))
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amount_ingredient',
        verbose_name='Ингредиент')

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_combination'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favorite')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe')


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopping')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_user')

    def __str__(self):
        return (f'пользователь {self.user.username}'
                f'имеет в списке покупок {self.recipe.name}')
