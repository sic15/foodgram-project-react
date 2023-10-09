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
from user.serializers import (PasswordSerializer, UserCreationSerializer,
                              UserReadSerializer)

from .filters import RecipeFilter
from .pagination import SubscribePagination
from .permissions import RecipePermission
from .serializers import (AmountIngredientSerializer, BaseRecipeSerializer,
                          IngredientSerializer, RecipeChangeSerializer,
                          RecipeReadSerializer, ShoppingCartSerializer,
                          SubscribeCreateSerializer, SubscribeSerializer,
                          TagSerializer)


class UserViewSet(DjoserUserViewSet):
    pagination_class = PageNumberPagination
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        return UserCreationSerializer

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
    permission_classes = (RecipePermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrive'):
            return RecipeReadSerializer
        return RecipeChangeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if not Favorite.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = BaseRecipeSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED)
        return Response({'errors': 'Рецепт уже в избранном.'},
                        status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        object = get_object_or_404(Favorite, user=request.user,
                                   recipe=recipe)
        object.delete()
        return Response({'detail': 'Рецепт успешно удален из избранного.'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if not ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = BaseRecipeSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED)
        return Response({'errors': 'Рецепт уже в списке покупок.'},
                        status=status.HTTP_400_BAD_REQUEST)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        object = get_object_or_404(ShoppingCart, user=request.user,
                                   recipe=recipe)
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
        data = {'user': id, 'author': pk}
        serializer = SubscribeCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        subscribe = get_object_or_404(Subscribe,
                                      user=self.request.user,
                                      author=get_object_or_404(
                                          User,
                                          id=pk))
        subscribe.delete()
        return Response({'message': 'Подписка успешно удалена.'},
                        status=status.HTTP_204_NO_CONTENT)


class APIShoppingCart(APIView):
    def get(self, request):
        carts = ShoppingCart.objects.filter(user=request.user)
        serializer = ShoppingCartSerializer(carts, many=True)
        return Response(serializer.data)
