from djoser.serializers import UserCreateSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from food.models import (AmountIngredient, Favorite, Ingredient, Recipe,
                         ShoppingCart, Tag)
from user.models import Subscribe, User


class UserReadSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed")

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Subscribe.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        return False


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'password')
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
        }

    def validate(self, obj):
        invalid_usernames = ['me', 'set_password',
                             'subscriptions', 'subscribe']
        if self.initial_data.get('username') in invalid_usernames:
            raise serializers.ValidationError(
                {'username': 'Вы не можете использовать этот username.'}
            )
        return obj


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


class PasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

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
        model = AmountIngredient
        fields = ('id', 'name',
                  'measurement_unit', 'amount')


class UserinfoSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            'is_subscribed')

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Subscribe.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        return False


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserinfoSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source='recipe')
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
        fields = ("id", 'name', "cooking_time", "image")


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
        RECIPES_MAX = Recipe.objects.filter(author=obj).count()
        if self.context:
            filter_value = self.context['request'].query_params.get(
                'recipes_limit', RECIPES_MAX)
            queryset = Recipe.objects.filter(author=obj)[:int(filter_value)]
        else:
            queryset = Recipe.objects.filter(author=obj)
        recipes = BaseRecipeSerializer(queryset, many=True)
        return recipes.data

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
        fields = "__all__"


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

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError(
                {'error': 'Количсетво ингредиента не может быть 0.'})
        return value


class RecipeChangeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = UserinfoSerializer(read_only=True)
    id = serializers.ReadOnlyField()
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients',
                  'image', "tags",
                  'name', 'text',
                  'cooking_time', 'author')

    def validate_cooking_time(self, value):
        if value == 0:
            raise serializers.ValidationError(
                {'error': 'Время приготовления не может быть 0.'})
        return value

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
            try:
                Ingredient.objects.get(id=item['id'])
            except BaseException:
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
        for ingredient in ingredients:
            id = ingredient['id']
            current_ingredient = Ingredient.objects.get(id=id)
            amount = ingredient['amount']
            AmountIngredient.objects.create(
                ingredient=current_ingredient, recipe=recipe, amount=amount)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
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
        for ingredient in ingredients:
            id = ingredient['id']
            current_ingredient = Ingredient.objects.get(id=id)
            amount = ingredient['amount']
            AmountIngredient.objects.create(
                ingredient=current_ingredient, recipe=instance, amount=amount)
        return instance
