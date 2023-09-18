from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from transliterate import translit

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=20)
   # color = models.Choices
    slug = models.SlugField(default='', null = True, blank = True)

    def save(self, *args, **kwargs):
        self.slug = slugify(translit(self.name, 'ru', reversed=True))
        super(Tag, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Ingredient(models.Model):
    MEASURE_CHOISES = [('g', 'г'), ('kg', 'кг'), ('l', 'л'), ('ml', 'мл'), ('piece', 'шт')]

    name = models.CharField(max_length=50)
    measure = models.CharField(max_length=5, choices=MEASURE_CHOISES)

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
    ingredients = models.ManyToManyField(Ingredient, through='Quantity')
    tag = models.ManyToManyField(Tag, related_name='recipe')
    

    def __str__(self):
        return self.name

class Quantity(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True)
    quantity = models.FloatField()
    measure = models.ForeignKey(Ingredient, on_delete=models.SET_NULL, null=True)





