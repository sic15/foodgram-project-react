from django_filters import rest_framework as filters

from food.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    author = filters.AllValuesFilter(field_name='author')
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all())
    is_favorited = filters.BooleanFilter(
        field_name="is_favorited",
        method='is_favorite_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name="is_in_shopping_cart",
        method='is_in_shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'author', 'tags', 'is_in_shopping_cart']

    def filter_tags(self, queryset, slug, tags):
        return queryset.filter(tags__slug__contains=tags.split(','))

    def is_favorite_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite__user=user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shoppingcart__user=user)
        return queryset
