from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from reviews_app.models import Review
from reviews_app.api.serializers import ReviewSerializer
from reviews_app.api.permissions import IsAuthenticatedOrCustomerCreateOrOwnerUpdateDelete
from reviews_app.api.filters import ReviewFilter


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for listing, creating, and updating reviews."""

    queryset = Review.objects.all().distinct()
    serializer_class = ReviewSerializer
    filterset_class = ReviewFilter
    permission_classes = [IsAuthenticatedOrCustomerCreateOrOwnerUpdateDelete]
    pagination_class = None
    ordering_fields = ["updated_at", "rating"]
    ordering = ["-updated_at"]

    def retrieve(self, request, *args, **kwargs):
        """Block GET on detail view (not allowed)."""
        if request.method == "GET":
            return Response({"detail": "GET is not allowed in detail View."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        """Block PUT, allow PATCH for updates."""
        if request.method == "PUT":
            return Response(
                {"detail": "PUT is not allowed. Use PATCH instead."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        else:
            return super().update(request, *args, **kwargs)
