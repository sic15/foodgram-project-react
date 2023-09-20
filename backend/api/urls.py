from django.urls import include, path
from rest_framework.routers import SimpleRouter, DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter() #SimpleRouter()
router.register('tags', views.TagViewSet, basename = 'tags')
router.register('recipes', views.RecipeViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('amount', views.AmountIngredientViewSet)
#router.register('users', views.UserViewSet)
#router.register('subscriptions', views.SubscribeViewSet)

urlpatterns = [
    
    path('users/<int:pk>/subscriptions/', views.APICreateSubscribe.as_view()),
    path('users/subscriptions/', views.APISubscribe.as_view()),
    path('users/<int:pk>/', views.APIUserInfo.as_view()),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('users/', views.APIUser.as_view()),
    path('', include(router.urls)),
]
