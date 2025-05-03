from django.db.models import Min
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from offers_app.models import Offer, OfferDetail
from offers_app.api.serializers import OfferSerializer, OfferDetailSerializer
from offers_app.api.filters import OfferFilter
from offers_app.api.pagination import OfferPagination
from offers_app.api.permissions import IsAuthenticatedOrBusinessCreateOrOwnerUpdateDelete


class OfferModelViewSet(ModelViewSet):
    queryset = Offer.objects.all().distinct().annotate(min_price=Min("details__price"))
    serializer_class = OfferSerializer
    filterset_class = OfferFilter
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]
    pagination_class = OfferPagination
    permission_classes = [IsAuthenticatedOrBusinessCreateOrOwnerUpdateDelete]


class OfferDetailViewSet(ReadOnlyModelViewSet):
    queryset = OfferDetail.objects.all().distinct()
    serializer_class = OfferDetailSerializer
    pagination_class = None
    lookup_field = "id"
