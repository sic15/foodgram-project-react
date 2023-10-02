from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from food.models import (AmountIngredient, Favorite, Ingredient, Recipe,
                         ShoppingCart, Tag)
from user.models import Subscribe, User

from .filters import RecipeFilter
from .pagination import SubscribePagination
from .permissions import IsAuthorChangeOnly
from .serializers import (AmountIngredientSerializer, BaseRecipeSerializer,
                          IngredientSerializer, PasswordSerializer,
                          RecipeChangeSerializer, RecipeReadSerializer,
                          ShoppingCartSerializer, SubscribeCreateSerializer,
                          SubscribeSerializer, TagSerializer,
                          UserCreateSerializer, UserReadSerializer)


class UserViewSet(DjoserUserViewSet):
    pagination_class = PageNumberPagination
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        return UserCreateSerializer

    @action(detail=False, methods=['get'],
            pagination_class=None,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = PasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        filter_value = self.request.query_params.get('name', None)
        if filter_value:
            queryset = queryset.filter(name__icontains=filter_value)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('id')
    permission_classes = (IsAuthorChangeOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrive'):
            return RecipeReadSerializer
        return RecipeChangeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=kwargs['pk'])
            except BaseException:
                return Response({'errors': 'Нет такого рецепта.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if not Favorite.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                Favorite.objects.create(user=request.user, recipe=recipe)
                serializer = BaseRecipeSerializer(recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=kwargs['pk'])
            try:
                object = Favorite.objects.get(user=request.user,
                                              recipe=recipe)
            except BaseException:
                return Response({'errors': 'Рецепт не был в избранном.'},
                                status=status.HTTP_400_BAD_REQUEST)
            object.delete()
            return Response({'detail': 'Рецепт успешно удален из избранного.'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get', 'post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=kwargs['pk'])
            except BaseException:
                return Response({'errors': 'Нет такого рецепта.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if not ShoppingCart.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                serializer = BaseRecipeSerializer(recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=kwargs['pk'])
            try:
                object = ShoppingCart.objects.get(user=request.user,
                                                  recipe=recipe)
            except BaseException:
                return Response({'errors': 'Нет такой подписки.'},
                                status=status.HTTP_400_BAD_REQUEST)
            object.delete()
            return Response({'detail': ('Рецепт успешно'
                             'удален из списка покупок.')},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            AmountIngredient.objects
            .filter(recipe__shopping_user__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        file_list = []
        [file_list.append(
            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients]
        file = HttpResponse('Cписок покупок:\n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = (
            'attachment; filename=shopping_cart.txt')
        return file


class AmountIngredientViewSet(viewsets.ModelViewSet):
    queryset = AmountIngredient.objects.all()
    serializer_class = AmountIngredientSerializer


class APISubscribe(generics.ListAPIView):
    serializer_class = SubscribeSerializer
    pagination_class = SubscribePagination

    def get_queryset(self):
        queryset = User.objects.filter(subscribing__user=self.request.user)
        return queryset


class APICreateDeleteSubscribe(APIView):
    def post(self, request, pk):
        id = self.request.user.id
        if id == pk:
            return Response({'errors': 'Нельзя подписаться на себя.'},
                            status=status.HTTP_400_BAD_REQUEST)
        author = get_object_or_404(User, id=pk)
        if Subscribe.objects.filter(
                user=self.request.user,
                author=author).exists():
            return Response({'errors': 'Подписка уже существует.'},
                            status=status.HTTP_400_BAD_REQUEST)

     #   x=self.request.query_params.get('recipes_limit')
        data = {'user': id, 'author': pk}
        serializer = SubscribeCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            subscribe = Subscribe.objects.get(
                user=self.request.user,
                author=get_object_or_404(
                    User,
                    id=pk))
        except ObjectDoesNotExist:
            return Response({'errors': 'Такой подписки не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)
        subscribe.delete()
        return Response({'message': 'Подписка успешно удалена.'},
                        status=status.HTTP_204_NO_CONTENT)


class APIShoppingCart(APIView):
    def get(self, request):
        carts = ShoppingCart.objects.filter(user=request.user)
        for cart in carts:
            recipe_id = cart.recipe.id
            recipe = get_object_or_404(Recipe, id=recipe_id)
            print(recipe.recipe.id)
        serializer = ShoppingCartSerializer(carts, many=True)
        return Response(serializer.data)
