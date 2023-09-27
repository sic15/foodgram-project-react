from django_filters import rest_framework as filters
from food.models import Recipe

class RecipeFilter(filters.FilterSet):
    author = filters.AllValuesFilter(field_name='author')
    tags=filters.AllValuesFilter(field_name='tags')
    is_favorite = filters.BooleanFilter(field_name="is_favorite", method='is_favorite_filter')
    is_in_shopping_cart = filters.BooleanFilter(field_name="is_in_shopping_cart", method='is_in_shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = ['is_favorite', 'author', 'tags', 'is_in_shopping_cart']

    def is_favorite_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite_recipe__user=user)
        return queryset
    
    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_user__user=user)
        return queryset