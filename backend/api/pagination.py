from rest_framework.pagination import LimitOffsetPagination

from user.models import User


class SubscribePagination(LimitOffsetPagination):
    limit_query_param = 'recipes'

    class Meta:
        model = User
