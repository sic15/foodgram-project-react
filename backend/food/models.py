from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from transliterate import translit

from foodgram_backend import constants as c
from user.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=c.FoodContant.MAX_TAG_NAME_LENGTH,
        verbose_name='Имя тэга')
    color = ColorField(verbose_name='Цвет')
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

    name = models.CharField(
        max_length=c.FoodContant.MAX_INGREDIENT_NAME,
        verbose_name='Название рецепта')
    measurement_unit = models.CharField(
        max_length=c.FoodContant.MAX_MEASUREMENT_UNIT_LENGTH,
        choices=MEASURE_CHOISES,
        verbose_name='Единица измерения')

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Игредиенты'
        unique_together = ['name', 'measurement_unit']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор')
    name = models.CharField(
        max_length=c.FoodContant.MAX_RECIPE_NAME_LENGHT,
        verbose_name='Название')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=(
            MinValueValidator(
                c.FoodContant.MIN_COOKING_TIME,
                f"Время приготовления не может быть"
                f"{c.FoodContant.MIN_COOKING_TIME}"),
            MaxValueValidator(
                c.FoodContant.MAX_COOKING_TIME,
                "Время приготовления не может быть таким большим")))
    image = models.ImageField(
        verbose_name='Картинка',
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
        verbose_name='Количество', validators=(
            MinValueValidator(
                c.FoodContant.MIN_AMOUNT,
                f'Количество не может быть {c.FoodContant.MIN_AMOUNT}'),))
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


class UniqueTogetherFields(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Автор')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Рецепт')

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'user',
                    'recipe'],
                name='%(class)s')]


class Favorite(UniqueTogetherFields):
    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(UniqueTogetherFields):
    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'

    def __str__(self):
        return (f'пользователь {self.user.username}'
                f'имеет в списке покупок {self.recipe.name}')
