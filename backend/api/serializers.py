from rest_framework import serializers
from food.models import Tag, Ingredient, Recipe, AmountIngredient, ShoppingCart, Favorite
from user.models import User, Subscribe


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmountIngredient
        fields = "__all__"

class AmountIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmountIngredient
        fields = '__all__'

class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    
    class Meta:
        model=AmountIngredient
        fields=('id', 'name',
                  'measurement_unit', 'amount')


class UserinfoSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name",'is_subscribed')

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Subscribe.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        return False


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserinfoSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, read_only=True, source='recipe')
   # ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        queryset=Ingredient.objects.filter(recipe=obj)
        serializer=RecipeIngredientSerializer(data=queryset,many=True)
        serializer.is_valid()
        return serializer.data

    def get_is_favorited(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Favorite.objects.filter(user=self.context['request'].user,
                                        recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and ShoppingCart.objects.filter(
                user=self.context['request'].user,
                recipe=obj).exists()
        )

class BaseRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "cooking_time", "image")
          

class SubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = BaseRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name",'is_subscribed', "recipes", "recipes_count")

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Subscribe.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        return False
    
    def get_recipes_count(self, obj):
        return obj.recipes.count()
    

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('favorite', 'user')

class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'