from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
#from django.conf.urls import url
from django.urls import re_path as url

admin.site.site_header = 'Админка учебного приложения FoodGram'
#admin.site.index_title = 'Администрирование сайта '

schema_view = get_schema_view(
   openapi.Info(
      title="Foodgram API",
      default_version='v1',
      description="Документация для приложения api проекта Foodgram",
      # terms_of_service="URL страницы с пользовательским соглашением",
      contact=openapi.Contact(email="sic15@yandex.ru"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)   

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('api/', include('api.urls')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', 
       schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), 
       name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), 
       name='schema-redoc'),
   # path('', include('food.urls')),
]
