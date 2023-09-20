from django.db import models
from django.utils.text import slugify
from transliterate import translit

from user.models import User

#User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=20)
   # color = models.Choices
    slug = models.SlugField(default='', null = True, blank = True)

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
    MEASURE_CHOISES = [('g', 'г'), ('kg', 'кг'), ('l', 'л'), ('ml', 'мл'), ('piece', 'шт')]

    name = models.CharField(max_length=50)
    measure = models.CharField(max_length=5, choices=MEASURE_CHOISES)
    
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
        related_name='recipe')
    name = models.CharField(max_length=50)
    description = models.TextField()
    cooking_time = models.IntegerField()
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        blank=True
    )
    ingredients = models.ManyToManyField(Ingredient, through='Quantity', through_fields=('recipe', 'measure'),)
    tag = models.ManyToManyField(Tag, related_name='recipe')
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        
    def __str__(self):
        return self.name

class Quantity(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Рецепт')
    quantity = models.FloatField("Количество")
    measure = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredients',
        verbose_name='Ингредиент')
    
    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'measure'],
                name='unique_combination'
            )
        ]

class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_recipe')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_user')

class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopping')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='shopping_user')





