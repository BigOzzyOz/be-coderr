from django.db.models import Min
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import status

# from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, NotFound, PermissionDenied
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

    def put(self, request, *args, **kwargs):
        return Response({"detail": "PUT is not allowed. Use PATCH instead."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # def destroy(self, request, *args, **kwargs):
    #     print("Destroy method called")
    #     try:
    #         instance = self.get_object()
    #         self.check_object_permissions(request, instance)
    #     except Exception as e:
    #         if isinstance(e, (AuthenticationFailed, NotAuthenticated)):
    #             return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    #         elif isinstance(e, NotFound):
    #             return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
    #         elif isinstance(e, PermissionDenied):
    #             return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
    #         else:
    #             return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OfferDetailViewSet(ReadOnlyModelViewSet):
    queryset = OfferDetail.objects.all().distinct()
    serializer_class = OfferDetailSerializer
    pagination_class = None
    lookup_field = "id"
