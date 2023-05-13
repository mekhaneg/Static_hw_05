from rest_framework.pagination import PageNumberPagination
from backend import settings


class CustomPagination(PageNumberPagination):
    page_size = settings.PAGINATOR_CONST
