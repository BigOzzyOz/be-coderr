from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from core.utils.test_client import JSONAPIClient
from offers_app.api.views import OfferDetailViewSet
from offers_app.models import Offer, OfferDetail


class TestOfferDetailDetailView(APITestCase):
    client_class = JSONAPIClient

    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pw123", email="u@mail.de")
        self.user.profile.type = "business"
        self.user.profile.save()
        self.offer = Offer.objects.create(user=self.user, title="Test", description="desc")
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Detail1",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["A"],
            offer_type="basic",
        )
        self.url = reverse("offerdetails-detail", kwargs={"id": self.detail.pk})

    def test_get_offerdetail_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_get_offerdetail_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.detail.pk)

    def test_get_offerdetail_not_found(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("offerdetails-detail", kwargs={"id": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_offerdetail_internal_server_error(self):
        self.client.force_authenticate(user=self.user)
        orig_get_queryset = OfferDetailViewSet.get_queryset

        def error_get_queryset(self):
            raise Exception("Test-Fehler")

        OfferDetailViewSet.get_queryset = error_get_queryset
        try:
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 500)
            self.assertIn("detail", response.data)
        finally:
            OfferDetailViewSet.get_queryset = orig_get_queryset
