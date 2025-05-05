from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from core.utils.test_client import JSONAPIClient
from offers_app.models import Offer


class TestOfferCreateView(APITestCase):
    client_class = JSONAPIClient

    def setUp(self):
        self.business_user = User.objects.create_user(username="business", password="pw123", email="b@mail.de")
        self.business_user.profile.type = "business"
        self.business_user.profile.save()
        self.customer_user = User.objects.create_user(username="customer", password="pw123", email="c@mail.de")
        self.customer_user.profile.type = "customer"
        self.customer_user.profile.save()
        self.url = reverse("offer-list")
        self.valid_data = {
            "title": "Neues Angebot",
            "description": "Beschreibung",
            "details": [
                {
                    "title": "Detail",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["A"],
                    "offer_type": "basic",
                }
            ],
        }

    def test_post_offer_unauthenticated(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 401)

    def test_post_offer_not_business(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 403)

    def test_post_offer_success(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.data)

    def test_post_offer_invalid_data(self):
        self.client.force_authenticate(user=self.business_user)
        data = {"title": "", "details": []}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)

    def test_post_offer_internal_server_error(self):
        self.client.force_authenticate(user=self.business_user)
        orig_create = Offer.objects.create
        Offer.objects.create = lambda *a, **kw: (_ for _ in ()).throw(Exception("Test-Fehler"))
        try:
            response = self.client.post(self.url, self.valid_data)
            self.assertEqual(response.status_code, 500)
        finally:
            Offer.objects.create = orig_create
