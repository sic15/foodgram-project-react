from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index),
    path('food/', views.food_list),
    path('food/<id>/', views.food_detail),
] 