from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets


from api import serializers
from food.models import Tag, Recipe, Ingredient, Quantity
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, QuantitySerializer


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer 

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

class QuantityViewSet(viewsets.ModelViewSet):
    queryset = Quantity.objects.all()
    serializer_class = QuantitySerializer


#@api_view(['GET', 'POST'])
#def recipe_list(request):
#    if request.method == 'POST':
#        serializer = serializers.RecipeSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#    recipes = Recipe.objects.all()
#    serializer = serializers.RecipeSerializer(recipes, many=True)
#    return Response(serializer.data) 