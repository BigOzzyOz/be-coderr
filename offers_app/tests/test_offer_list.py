from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from core.utils.test_client import JSONAPIClient
from offers_app.models import Offer, OfferDetail


class TestOfferListView(APITestCase):
    """Tests for offer list API endpoints."""

    client_class = JSONAPIClient

    @classmethod
    def setUpTestData(cls):
        cls.business_user = User.objects.create_user(username="business", password="pw123", email="b@mail.de")
        cls.business_user.profile.type = "business"
        cls.business_user.profile.save()
        cls.customer_user = User.objects.create_user(username="customer", password="pw123", email="c@mail.de")
        cls.customer_user.profile.type = "customer"
        cls.customer_user.profile.save()
        cls.offer = Offer.objects.create(user=cls.business_user, title="Test", description="desc")
        OfferDetail.objects.create(
            offer=cls.offer,
            title="Detail1",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["A"],
            offer_type="basic",
        )
        cls.url = reverse("offer-list")

    def setUp(self):
        self.client = self.client_class()

    def test_get_offer_list_unauthenticated(self):
        """Test that unauthenticated users can list offers."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)

    def test_get_offer_list_authenticated(self):
        """Test that authenticated users can list offers."""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)

    def test_get_offer_list_invalid_query(self):
        """Test that invalid query params return 400."""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.url + "?min_price=abc")
        self.assertEqual(response.status_code, 400)
        self.assertIn("min_price", str(response.data))

    def test_get_offer_list_internal_server_error(self):
        """Test that server error during list returns exception."""
        self.client.force_authenticate(user=self.customer_user)
        orig_list = self.client.get

        def error_list(*a, **kw):
            raise Exception("Test-Fehler")

        self.client.get = error_list
        try:
            with self.assertRaises(Exception):
                self.client.get(self.url)
        finally:
            self.client.get = orig_list
