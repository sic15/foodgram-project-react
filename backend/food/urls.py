from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('food/', views.food_list),
    path('food/<id>/', views.food_detail),
]
