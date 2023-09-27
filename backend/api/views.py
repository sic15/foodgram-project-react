from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status, generics, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response


from food.models import Tag, Recipe, Ingredient, AmountIngredient, Favorite, ShoppingCart
from .serializers import TagSerializer, IngredientSerializer, RecipeReadSerializer, AmountIngredientSerializer, UserinfoSerializer, SubscribeSerializer, FavoriteSerializer, ShoppingCartSerializer, SubscribeCreateSerializer, RecipeChangeSerializer
from user.models import User, Subscribe
from .filters import RecipeFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer 
    pagination_class=None

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class=None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
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
        print('запущена функция списка покупок')
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            if not Favorite.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                Favorite.objects.create(user=request.user, recipe=recipe)
                return Response({'detail': 'Рецепт успешно добавлен в избранное.'},
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(Favorite, user=request.user,
                              recipe=recipe).delete()
            return Response({'detail': 'Рецепт успешно удален из избранного.'},
                            status=status.HTTP_204_NO_CONTENT)
        
    @action(detail=True, methods=['get', 'post', 'delete'],
        permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            if not ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                return Response({'detail': 'Рецепт успешно добавлен в список покупок.'},
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if request.method == 'DELETE':
            get_object_or_404(ShoppingCart, user=request.user,
                              recipe=recipe).delete()
            return Response({'detail': 'Рецепт успешно удален из списка покупок.'},
                            status=status.HTTP_204_NO_CONTENT)
        
    
    @action(detail=False, methods=['get'],)
           # permission_classes=(IsAuthenticated,))
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

    def get_queryset(self):
        queryset = User.objects.filter(subscribing__user=self.request.user)
        return queryset


class APICreateDeleteSubscribe(APIView):
    def post(self, request, pk):
        id = self.request.user.id
        if id == pk:
            return Response({'errors': 'Нельзя подписаться на себя.'}, status=status.HTTP_400_BAD_REQUEST)
        author = User.objects.get(id=pk)
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


class APIUser(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserinfoSerializer
    pagination_class = PageNumberPagination

class APIUserInfo(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserinfoSerializer

class APIShoppingCart(APIView):
    def get(self, request):
        carts = ShoppingCart.objects.filter(user = request.user)
        for cart in carts:
            recipe_id = cart.recipe.id
            recipe = get_object_or_404(Recipe, id=recipe_id)
            print(recipe.recipe.id)
        serializer = ShoppingCartSerializer(carts, many=True)
        return Response(serializer.data)