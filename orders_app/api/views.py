from django.db import models
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from orders_app.models import Order
from orders_app.api.serializers import OrderSerializer
from orders_app.api.permissions import IsAuthenticatedOrCustomerCreateOrBusinessUpdateOrStaffDelete


class OrderModelViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrCustomerCreateOrBusinessUpdateOrStaffDelete]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().order_by("-created_at")
        else:
            return Order.objects.filter(models.Q(customer_user=user) | models.Q(business_user=user)).order_by(
                "-created_at"
            )

    def retrieve(self, request, *args, **kwargs):
        return Response({"detail": "GET is not allowed in detail view."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        if request.method == "PUT":
            return Response(
                {"detail": "PUT is not allowed. Use PATCH instead."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        else:
            return super().update(request, *args, **kwargs)


class BusinessOrderCountView(APIView):
    def get(self, request, business_user_id, *args, **kwargs):
        count = Order.objects.filter(business_user_id=business_user_id).count()
        return Response({"order_count": count})


class BusinessOrderCompleteCountView(APIView):
    def get(self, request, business_user_id, *args, **kwargs):
        count = Order.objects.filter(business_user_id=business_user_id, status="completed").count()
        return Response({"completed_order_count": count})
