from django.db.models import Min
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import status
from offers_app.models import Offer, OfferDetail
from offers_app.api.serializers import OfferSerializer, OfferDetailSerializer
from offers_app.api.filters import OfferFilter
from offers_app.api.pagination import OfferPagination
from offers_app.api.permissions import IsAuthenticatedOrBusinessCreateOrOwnerUpdateDelete


class OfferModelViewSet(ModelViewSet):
    """ViewSet for listing, creating, updating, and deleting offers."""

    queryset = Offer.objects.all().distinct().annotate(min_price=Min("details__price"))
    serializer_class = OfferSerializer
    filterset_class = OfferFilter
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]
    pagination_class = OfferPagination
    permission_classes = [IsAuthenticatedOrBusinessCreateOrOwnerUpdateDelete]

    def update(self, request, *args, **kwargs):
        """Handle PATCH update, block PUT requests."""
        if request.method == "PUT":
            return Response(
                {"detail": "PUT is not allowed. Use PATCH instead."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        else:
            return super().update(request, *args, **kwargs)


class OfferDetailViewSet(ReadOnlyModelViewSet):
    """Read-only ViewSet for offer details."""

    queryset = OfferDetail.objects.all().distinct()
    serializer_class = OfferDetailSerializer
    pagination_class = None
    lookup_field = "id"
