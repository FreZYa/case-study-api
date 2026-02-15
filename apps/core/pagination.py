from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Project-wide pagination with configurable page size."""

    page_size = 10
    page_size_query_param = "per_page"
    max_page_size = 100
