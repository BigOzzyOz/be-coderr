from rest_framework.routers import DefaultRouter
from offers_app.api.views import OfferModelViewSet, OfferDetailViewSet

router = DefaultRouter()
router.register(r"offers", OfferModelViewSet, basename="offer")
router.register(r"offerdetails", OfferDetailViewSet, basename="offerdetails")

urlpatterns = []

urlpatterns += router.urls
