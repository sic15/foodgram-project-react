from rest_framework import serializers
from food.models import Tag, Ingredient, Recipe, Quantity
from user.models import User, Subscribe
#from djoser.serializers import UserSerializer

#from food.models import Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'

class UserinfoSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name",'is_subscribed') # "is_subscribed")

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Subscribe.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        return False

class RecipeSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=True, read_only=True)
    author = UserinfoSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    class Meta:
        model = Recipe
        fields = '__all__'

class QuantitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Quantity
        fields = '__all__'


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('favorite', 'user')