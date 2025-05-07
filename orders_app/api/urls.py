from django.urls import path
from rest_framework.routers import DefaultRouter
from orders_app.api.views import OrderModelViewSet, BusinessOrderCountView, BusinessOrderCompleteCountView

router = DefaultRouter()
router.register(r"orders", OrderModelViewSet, basename="order")

urlpatterns = [
    path("order-count/<int:business_user_id>/", BusinessOrderCountView.as_view(), name="business-order-count"),
    path(
        "completed-order-count/<int:business_user_id>/",
        BusinessOrderCompleteCountView.as_view(),
        name="business-order-complete-count",
    ),
]

urlpatterns += router.urls
