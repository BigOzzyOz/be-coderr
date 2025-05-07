from rest_framework.routers import DefaultRouter
from orders_app.api.views import OrderModelViewSet

router = DefaultRouter()
router.register(r"orders", OrderModelViewSet, basename="order")

urlpatterns = []

urlpatterns += router.urls
