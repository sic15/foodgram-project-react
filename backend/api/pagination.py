from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from user.models import User

class SubscribePagination(LimitOffsetPagination):#PageNumberPagination):
    limit_query_param = 'recipes'
    class Meta:
        model = User