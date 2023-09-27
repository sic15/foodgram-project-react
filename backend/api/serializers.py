
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from food.models import Tag, Ingredient, Recipe, AmountIngredient, ShoppingCart, Favorite
from user.models import User, Subscribe

class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name", "is_subscribed")

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Subscribe.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")
        read_only_fields=("name", "color", "slug")

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"

class AmountIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmountIngredient
        fields = '__all__'

class PasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()
 #   class Meta:
 #       model = User
 #       fields = ('new_password', 'current_password')

  #  def validate(self, obj):
  #      try:
  #          validate_password(obj['new_password'])
  #      except django_exceptions.ValidationError as e:
  #          raise serializers.ValidationError(
  #              {'new_password': list(e.messages)}
  #          )
  #      return super().validate(obj)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Неверный текущий пароль.'}
            )
        if (validated_data['current_password']
           == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data

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


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserinfoSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, read_only=True, source='recipe')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    class Meta:
        model = Recipe
        fields = '__all__'

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
    
class BaseSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"#("email", "id", "username", "first_name", "last_name",'is_subscribed', "recipes", "recipes_count")


class SubscribeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = '__all__'

    def to_representation(self, instance):
        serializer = SubscribeSerializer(instance.author)
        return serializer.data 


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('favorite', 'user')

class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'

class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount')


class RecipeChangeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = UserinfoSerializer(read_only=True)
    id = serializers.ReadOnlyField()
    ingredients = RecipeIngredientCreateSerializer(many=True)
   # image = Base64ImageField(blank=True)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients',
                 'image',"tags",
                  'name', 'text',
                  'cooking_time', 'author')
        
    def to_representation(self, instance):
        request = self.context.get('request')
        serializer = RecipeReadSerializer(instance, context={'request':request})
        return serializer.data        
        
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            id = ingredient['id']
            current_ingredient = Ingredient.objects.get(id = id)
            amount = ingredient['amount']
            AmountIngredient.objects.create(
                ingredient=current_ingredient, recipe=recipe, amount=amount)
        recipe.tags.set(tags)
        return recipe

        
    