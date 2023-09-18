from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

app_name = 'api'

router = SimpleRouter()
router.register('tags', views.TagViewSet)
router.register('recipes', views.RecipeViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('quantitys', views.QuantityViewSet)

urlpatterns = [
    path('', include(router.urls)),
  #  path('recipe/', views.recipe_list)
 #   path('v1/', include('djoser.urls')),
  #  path('v1/', include('djoser.urls.jwt')),
]