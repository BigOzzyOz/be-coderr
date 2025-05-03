from django.db.models import Q
from django_filters import rest_framework as filters
from offers_app.models import Offer


class OfferFilter(filters.FilterSet):
    creator_id = filters.NumberFilter(field_name="user__id", lookup_expr="exact")
    min_price = filters.NumberFilter(field_name="details__price", lookup_expr="gte")
    max_delivery_time = filters.NumberFilter(field_name="details__delivery_time_in_days", lookup_expr="lte")
    search = filters.CharFilter(method="filter_search")

    class Meta:
        model = Offer
        fields = []

    def filter_search(self, queryset, name, value):
        terms = value.split()
        q = Q()
        for term in terms:
            q |= Q(title__icontains=term) | Q(description__icontains=term)
        return queryset.filter(q)
