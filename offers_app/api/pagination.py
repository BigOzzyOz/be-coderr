from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """Pagination for offers with custom page size and query params."""

    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 1000
    page_query_param = "page"
