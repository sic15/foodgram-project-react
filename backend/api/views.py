from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets, status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.decorators import action


from api import serializers
from food.models import Tag, Recipe, Ingredient, Quantity, Favorite
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, QuantitySerializer, UserinfoSerializer, SubscribeSerializer, FavoriteSerializer
from user.models import User, Subscribe

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer 

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class=None

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination

    @action(detail=True, methods=['post', 'delete'],)
           # permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
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

class QuantityViewSet(viewsets.ModelViewSet):
    queryset =Quantity.objects.all()
    serializer_class = QuantitySerializer

  #  def get_queryset(self):
  #      queryset = Quantity.objects.filter(recipe = self.recipe)
  #      return queryset


#class UserViewSet(viewsets.ModelViewSet):
#    queryset = User.objects.all()
#    serializer_class = UserSerializer
    
class APISubscribe(generics.ListAPIView):
    queryset = Subscribe.objects.all()
    serializer_class = SubscribeSerializer


class APICreateSubscribe(APIView):
    
    def post(self, request, pk):
        id = self.request.user.id
        data = {'user':id, 'author': pk}
        serializer = SubscribeSerializer(data=data)
        if serializer.is_valid() and id!=pk:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        if id == pk:
            return Response({'errors': 'Нельзя подписаться на себя.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    
    def delete(self, request, pk):
        subscribe = Subscribe.objects.get(user=self.request.user, author=get_object_or_404(User, id=pk) )
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class APIUser(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserinfoSerializer
    pagination_class = PageNumberPagination

class APIUserInfo(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserinfoSerializer

