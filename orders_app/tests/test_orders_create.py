from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from offers_app.models import Offer, OfferDetail
from core.utils.test_client import JSONAPIClient


class OrdersCreateAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user(username="kunde", password="pass1234", email="kunde@mail.de")
        cls.customer.profile.type = "customer"
        cls.customer.profile.save()
        cls.business = User.objects.create_user(username="business", password="pass1234", email="business@mail.de")
        cls.business.profile.type = "business"
        cls.business.profile.save()
        cls.other = User.objects.create_user(username="other", password="pass1234", email="other@mail.de")
        cls.other.profile.type = "business"
        cls.other.profile.save()
        cls.offer = Offer.objects.create(user=cls.business, title="Logo Design", description="Test Offer")
        cls.offer_detail = OfferDetail.objects.create(
            offer=cls.offer,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo Design", "Visitenkarten"],
            offer_type="basic",
        )

    def setUp(self):
        self.client = JSONAPIClient()

    def test_create_order_as_customer(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post("/api/orders/", {"offer_detail_id": self.offer_detail.id})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["customer_user"], self.customer.id)
        self.assertEqual(response.data["business_user"], self.business.id)

    def test_create_order_as_business_forbidden(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.post("/api/orders/", {"offer_detail_id": self.offer_detail.id})
        self.assertEqual(response.status_code, 403)

    def test_create_order_unauthenticated(self):
        response = self.client.post("/api/orders/", {"offer_detail_id": self.offer_detail.id})
        self.assertEqual(response.status_code, 401)

    def test_create_order_invalid_offer_detail(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post("/api/orders/", {"offer_detail_id": 9999})
        self.assertEqual(response.status_code, 404)

    def test_create_order_missing_offer_detail(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post("/api/orders/", {})
        self.assertEqual(response.status_code, 400)
