from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

from foodgram_backend import constants as c
from user.models import User 

 
class SubscribePagination(LimitOffsetPagination): 
    limit_query_param = 'recipes' 

    class Meta: 
        model = User


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = c.FoodContant.PAGE_SIZE
