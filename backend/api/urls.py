from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register('tags', views.TagViewSet, basename = 'tags')
router.register('recipes', views.RecipeViewSet)
router.register('ingredients', views.IngredientViewSet, basename='ingredients')
router.register('users', views.UserViewSet)

urlpatterns = [
    path('users/<int:pk>/subscribe/', views.APICreateDeleteSubscribe.as_view()),
    path('users/subscriptions/', views.APISubscribe.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),

    path('', include(router.urls)),
]
"""
  4dc2258445b32f4d3c0c9c13c042b910e7ef69b4
 "email": "s30@ya.ru",
    "password": "Qazxcvbnm1",
    "username": "sic30"
    
"""