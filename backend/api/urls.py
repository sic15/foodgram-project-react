from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register('tags', views.TagViewSet, basename = 'tags')
router.register('recipes', views.RecipeViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('users', views.UserViewSet)

urlpatterns = [
    path('users/<int:pk>/subscribe/', views.APICreateDeleteSubscribe.as_view()),
    path('users/subscriptions/', views.APISubscribe.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
