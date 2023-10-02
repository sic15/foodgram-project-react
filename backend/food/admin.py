from django.contrib import admin

from .models import AmountIngredient, Ingredient, Recipe, Tag

admin.site.register(Ingredient)
admin.site.register(AmountIngredient)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'author']
    list_filter = ['author', 'name', 'tags']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fields = ['name', 'color']
