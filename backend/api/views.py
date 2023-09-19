from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets, status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView


from api import serializers
from food.models import Tag, Recipe, Ingredient, Quantity
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, QuantitySerializer, UserinfoSerializer, SubscribeSerializer
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
        data = {'user':self.request.user.id, 'author': pk}
        serializer = SubscribeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
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

