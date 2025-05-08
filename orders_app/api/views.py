from django.db import models
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from orders_app.models import Order
from orders_app.api.serializers import OrderSerializer
from orders_app.api.permissions import IsAuthenticatedOrCustomerCreateOrBusinessUpdateOrStaffDelete
from django.contrib.auth.models import User


class OrderModelViewSet(viewsets.ModelViewSet):
    """ViewSet for listing, creating, updating, and deleting orders."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrCustomerCreateOrBusinessUpdateOrStaffDelete]
    pagination_class = None

    def get_queryset(self):
        """Return queryset filtered by user role (staff, customer, business)."""
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().order_by("-created_at")
        else:
            return Order.objects.filter(models.Q(customer_user=user) | models.Q(business_user=user)).order_by(
                "-created_at"
            )

    def retrieve(self, request, *args, **kwargs):
        """Block GET on detail view (not allowed)."""
        return Response({"detail": "GET is not allowed in detail view."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        """Block PUT, allow PATCH for updates."""
        if request.method == "PUT":
            return Response(
                {"detail": "PUT is not allowed. Use PATCH instead."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        else:
            return super().update(request, *args, **kwargs)


class BusinessOrderCountView(APIView):
    """API view to get count of in-progress orders for a business user."""

    def get(self, request, business_user_id, *args, **kwargs):
        """Return count of in-progress orders for given business user."""
        if not User.objects.filter(id=business_user_id, profile__type="business").exists():
            return Response({"detail": "Business user not found."}, status=status.HTTP_404_NOT_FOUND)
        count = Order.objects.filter(business_user_id=business_user_id, status="in_progress").count()
        return Response({"order_count": count})


class BusinessOrderCompleteCountView(APIView):
    """API view to get count of completed orders for a business user."""

    def get(self, request, business_user_id, *args, **kwargs):
        """Return count of completed orders for given business user."""
        if not User.objects.filter(id=business_user_id, profile__type="business").exists():
            return Response({"detail": "Business user not found."}, status=status.HTTP_404_NOT_FOUND)
        count = Order.objects.filter(business_user_id=business_user_id, status="completed").count()
        return Response({"completed_order_count": count})
