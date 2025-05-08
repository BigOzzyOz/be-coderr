from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from core.utils.test_client import JSONAPIClient
from offers_app.api.views import OfferDetailViewSet
from offers_app.models import Offer, OfferDetail


class TestOfferDetailDetailView(APITestCase):
    """Tests for OfferDetailViewSet (offerdetails-detail endpoint)."""
    client_class = JSONAPIClient

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="user", password="pw123", email="u@mail.de")
        cls.user.profile.type = "business"
        cls.user.profile.save()
        cls.offer = Offer.objects.create(user=cls.user, title="Test", description="desc")
        cls.detail = OfferDetail.objects.create(
            offer=cls.offer,
            title="Detail1",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["A"],
            offer_type="basic",
        )
        cls.url = reverse("offerdetails-detail", kwargs={"id": cls.detail.pk})

    def setUp(self):
        self.client = self.client_class()

    def test_get_offerdetail_unauthenticated(self):
        """Test unauthenticated users cannot access offer detail."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_get_offerdetail_authenticated(self):
        """Test authenticated user can access offer detail."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.detail.pk)

    def test_get_offerdetail_not_found(self):
        """Test 404 returned for non-existent offer detail."""
        self.client.force_authenticate(user=self.user)
        url = reverse("offerdetails-detail", kwargs={"id": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_offerdetail_internal_server_error(self):
        """Test 500 returned for server error in get_queryset."""
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
