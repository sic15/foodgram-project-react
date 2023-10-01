from django.contrib import admin
from .models import Recipe, Tag, Ingredient, AmountIngredient


admin.site.register(Ingredient)
#admin.site.register(Tag)
admin.site.register(AmountIngredient)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
   # fields = ['author', 'name', 'description', 'cooking_time', 'image', 'ingredients', 'tag']
    list_display = ['name', 'author']
    list_filter = ['author', 'name', 'tags']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fields=['name', 'color']