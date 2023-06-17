from rest_framework.pagination import PageNumberPagination


class LimitPageNumerPagination(PageNumberPagination):
    """Кастомизированный класс пагинации."""

    page_size_query_param = 'limit'
