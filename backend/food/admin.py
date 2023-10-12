from django.contrib import admin

from .models import AmountIngredient, Favorite, Ingredient, Recipe, Tag

admin.site.register(Ingredient)
admin.site.register(Favorite)
"""
class AmountInline(admin.StackedInline):
    model = AmountIngredient
    readonly_fields = ('measurement_unit', )
    fields = ['recipe', 'ingredient', ('amount', 'measurement_unit')]

    def measurement_unit(self, obj):
        return obj.ingredient.measurement_unit
"""
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('sudscriptions',)
    fields = ['author', 'name', 'text',
              'cooking_time', 'image', 'tags', 'sudscriptions']
    list_display = ['name', 'author']
    list_filter = ['author', 'name', 'tags']
 #   inlines = [AmountInline]

    def sudscriptions(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fields = ['name', 'color']

#admin.site.register(AmountIngredient)


@admin.register(AmountIngredient)
class AmountIngredientAdmin(admin.ModelAdmin):
    readonly_fields = ('measurement_unit', )
    fields = ['recipe', 'ingredient', ('amount', 'measurement_unit')]

    def measurement_unit(self, obj):
        return obj.ingredient.measurement_unit
    measurement_unit.short_description = ''
