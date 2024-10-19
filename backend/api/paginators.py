from rest_framework.pagination import PageNumberPagination


class CustomHomePagination(PageNumberPagination):
    """Пагинация рецептов. 6 штук на старнице."""

    page_size_query_param = 'limit'
