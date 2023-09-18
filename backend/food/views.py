from django.shortcuts import render
from rest_framework import viewsets 


# Create your views here.
def index(request):
    print('тратата')
    return render(request, 'food/index.html')

def food_list(request):
    return render(request, 'food/food_list.html')

def food_detail(request, id):
    return render(request, 'food/food_detail.html')