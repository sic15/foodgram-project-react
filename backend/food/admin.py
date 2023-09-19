from django.contrib import admin
from .models import Recipe, Tag, Ingredient, Quantity


admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Quantity)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
   # fields = ['author', 'name', 'description', 'cooking_time', 'image', 'ingredients', 'tag']
    list_display = ['name', 'author']
    list_filter = ['author', 'name', 'tag']