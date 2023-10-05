from django.contrib import admin

from .models import AmountIngredient, Favorite, Ingredient, Recipe, Tag

admin.site.register(AmountIngredient)
admin.site.register(Favorite)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('sudscriptions',)
    fields = ['author', 'name', 'text',
              'cooking_time', 'image', 'tags', 'sudscriptions']
    list_display = ['name', 'author']
    list_filter = ['author', 'name', 'tags']

    def sudscriptions(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fields = ['name', 'color']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_filter = ['name']
