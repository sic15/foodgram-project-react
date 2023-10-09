from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from food.models import (AmountIngredient, Favorite, Ingredient, Recipe,
                         ShoppingCart, Tag)
from foodgram_backend import constants as c
from user.models import Subscribe, User
from user.serializers import UserReadSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")
        read_only_fields = ("name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
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
        model = AmountIngredient
        fields = ('id', 'name',
                  'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserReadSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source='recipe')
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorite(self, obj):
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
        fields = ("id", 'name', "cooking_time", "image")


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if not value:
            raise serializers.ValidationError(
                {'error': 'Количсетво ингредиента не может быть 0.'})
        return value


class RecipeChangeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = UserReadSerializer(read_only=True)
    id = serializers.ReadOnlyField()
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField(required=True, allow_null=False)
    cooking_time = serializers.IntegerField(
        min_value=c.FoodContant.MIN_COOKING_TIME,
        max_value=c.FoodContant.MAX_COOKING_TIME)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients',
                  'image', "tags",
                  'name', 'text',
                  'cooking_time', 'author')

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError({'error': 'Добавьте картинку.'})
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                {'error': 'Добавьте хотя бы 1 тэг.'})
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                {'error': 'Тэги не должны повторяться.'})
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                {'error': 'Нельзя создать рецепт без ингредиентов.'}
            )
        for item in value:
            if not Ingredient.objects.filter(id=item['id']).exists():
                raise serializers.ValidationError(
                    {'error': 'Нет таких ингредиентов в базе данных.'}
                )
        id_list = [i['id'] for i in value]
        if len(id_list) != len(set(id_list)):
            raise serializers.ValidationError(
                {'error': 'Ингредиенты не должны повторяться.'})

        return value

    def to_representation(self, instance):
        request = self.context.get('request')
        serializer = RecipeReadSerializer(
            instance, context={'request': request})
        return serializer.data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        AmountIngredient.objects.bulk_create(
            [
                AmountIngredient(
                    ingredient=Ingredient.objects.get(id=ingredient['id']),
                    recipe=recipe,
                    amount=ingredient['amount']
                )
                for ingredient in ingredients
            ]
        )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = (validated_data.get('name', instance.name))
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        try:
            tags = validated_data.pop('tags')
        except BaseException:
            raise serializers.ValidationError(
                {'error': 'Добавьте хотя бы один тэг.'})
        instance.tags.set(tags)
        try:
            ingredients = validated_data.pop('ingredients')
        except BaseException:
            raise serializers.ValidationError(
                {'error': 'Добавьте хотя бы один ингредиент.'})
        AmountIngredient.objects.filter(recipe=instance).delete()
        AmountIngredient.objects.bulk_create(
            [
                AmountIngredient(
                    ingredient=Ingredient.objects.get(id=id),
                    recipe=instance,
                    amount=ingredient['amount']
                )
                for ingredient in ingredients
            ]
        )
        instance.save()
        return instance


class SubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            'is_subscribed',
            "recipes",
            "recipes_count")

    def get_recipes(self, obj):
        recipes_max = Recipe.objects.filter(author=obj).count()
        if self.context:
            filter_value = self.context['request'].query_params.get(
                'recipes_limit', recipes_max)
            queryset = Recipe.objects.filter(author=obj)[:int(filter_value)]
        else:
            queryset = Recipe.objects.filter(author=obj)
        recipes = BaseRecipeSerializer(queryset, many=True)
        return recipes.data

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if request and not request.user.is_anonymous:
            return Subscribe.objects.filter(user=request.user,
                                            author=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class BaseSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class SubscribeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = '__all__'

    def validate(self, data):
        if data['user'].id == data['author'].id:
            raise serializers.ValidationError(
                {'error': 'Нельзя подписаться на себя.'})

        if Subscribe.objects.filter(
                user=data['user'],
                author=data['author']).exists():
            raise serializers.ValidationError(
                {'error': 'Подписка уже существует.'})
        return data

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
