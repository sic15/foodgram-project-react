from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics, status, filters
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet

from food.models import Tag, Recipe, Ingredient, AmountIngredient, Favorite, ShoppingCart
from .serializers import (TagSerializer, IngredientSerializer, 
                          RecipeReadSerializer, AmountIngredientSerializer, 
                          UserinfoSerializer, SubscribeSerializer, 
                          ShoppingCartSerializer, SubscribeCreateSerializer, 
                          RecipeChangeSerializer, PasswordSerializer, UserReadSerializer,
                          UserCreateSerializer, BaseRecipeSerializer)
from user.models import User, Subscribe
from .filters import RecipeFilter
from .permissions import IsAuthorChangeOnly
from .pagination import SubscribePagination

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
    pagination_class=None

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class=None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        filter_value = self.request.query_params.get('name', None)
        if filter_value:
            queryset = queryset.filter(name__icontains=filter_value)
        return queryset

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorChangeOnly,)

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
            except:
                return Response({'errors': 'Нет такого рецепта.'},
                            status=status.HTTP_400_BAD_REQUEST)
            if not Favorite.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                Favorite.objects.create(user=request.user, recipe=recipe)
             #   data={"name":recipe.name, "cooking_time":recipe.cooking_time, "image":recipe.image}
                serializer=BaseRecipeSerializer(recipe)
             #   serializer.is_valid()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
              #  return Response({'detail': 'Рецепт успешно добавлен в избранное.'},
              #                  status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=kwargs['pk'])
            try:
                object = Favorite.objects.get(user=request.user,
                              recipe=recipe)
            except:
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
            except:
                return Response({'errors': 'Нет такого рецепта.'},
                            status=status.HTTP_400_BAD_REQUEST)
            if not ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                serializer=BaseRecipeSerializer(recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            #    return Response({'detail': 'Рецепт успешно добавлен в список покупок.'},
            #                    status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=kwargs['pk'])
            try:
                object = ShoppingCart.objects.get(user=request.user,
                              recipe=recipe)
            except:
                return Response({'errors':'Нет такой подписки.'},
                               status=status.HTTP_400_BAD_REQUEST)   
            object.delete()
            return Response({'detail': 'Рецепт успешно удален из списка покупок.'},
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
        file['Content-Disposition'] = (f'attachment; filename=shopping_cart.txt')
        return file

class AmountIngredientViewSet(viewsets.ModelViewSet):
    queryset =AmountIngredient.objects.all()
    serializer_class = AmountIngredientSerializer

    
class APISubscribe(generics.ListAPIView):
    serializer_class = SubscribeSerializer
    pagination_class = SubscribePagination

    def get_queryset(self):
        queryset = User.objects.filter(subscribing__user=self.request.user)
        return queryset
    
  #  def get(self, request):
  #      pages = self.paginate_queryset(
  #          User.objects.filter(subscribing__user=self.request.user)
  #      )
  #      serializer = SubscribeSerializer(pages, many=True)
  #      return self.get_paginated_response(serializer.data)


class APICreateDeleteSubscribe(APIView):
 #   pagination_class = LimitOffsetPagination

    def post(self, request, pk):
        id = self.request.user.id
        paginator = LimitOffsetPagination()
        if id == pk:
            return Response({'errors': 'Нельзя подписаться на себя.'}, status=status.HTTP_400_BAD_REQUEST)
        author = get_object_or_404(User, id=pk)
        if Subscribe.objects.filter(user=self.request.user, author = author).exists():
            return Response({'errors': 'Подписка уже существует.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {'user':id, 'author': pk}
        serializer = SubscribeCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    
    def delete(self, request, pk):
        try:
            subscribe = Subscribe.objects.get(user=self.request.user, author=get_object_or_404(User, id=pk))
        except ObjectDoesNotExist:
            return Response({'errors': 'Такой подписки не существует.'}, status=status.HTTP_400_BAD_REQUEST)
        subscribe.delete()
        return Response({'message': 'Подписка успешно удалена.'}, status=status.HTTP_204_NO_CONTENT)

"""
class APIUser(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserinfoSerializer
    pagination_class = PageNumberPagination

    @action(detail=True, methods=['post'])
    def set_password(self, request):
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.password = serializer.validated_data['password']
            user.save()
            return Response({'status': 'password set'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

class APIUserInfo(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserinfoSerializer
 """   

class APIShoppingCart(APIView):
    def get(self, request):
        carts = ShoppingCart.objects.filter(user = request.user)
        for cart in carts:
            recipe_id = cart.recipe.id
            recipe = get_object_or_404(Recipe, id=recipe_id)
            print(recipe.recipe.id)
        serializer = ShoppingCartSerializer(carts, many=True)
        return Response(serializer.data)
