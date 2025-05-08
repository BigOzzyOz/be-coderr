from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from core.utils.test_client import JSONAPIClient


class OrdersListAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user(username="kunde", password="pass1234", email="kunde@mail.de")
        cls.customer.profile.type = "customer"
        cls.customer.profile.save()
        cls.business = User.objects.create_user(username="business", password="pass1234", email="business@mail.de")
        cls.business.profile.type = "business"
        cls.business.profile.save()
        cls.other = User.objects.create_user(username="other", password="pass1234", email="other@mail.de")
        cls.other.profile.type = "customer"
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
        cls.order = Order.objects.create(
            customer_user=cls.customer,
            business_user=cls.business,
            title=cls.offer_detail.title,
            revisions=cls.offer_detail.revisions,
            delivery_time_in_days=cls.offer_detail.delivery_time_in_days,
            price=cls.offer_detail.price,
            features=cls.offer_detail.features,
            offer_type=cls.offer_detail.offer_type,
            status="in_progress",
        )

    def setUp(self):
        self.client = JSONAPIClient()

    def test_orders_list_authenticated_customer(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(o["id"] == self.order.id for o in response.data))

    def test_orders_list_authenticated_business(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(o["id"] == self.order.id for o in response.data))

    def test_orders_list_authenticated_other(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(any(o["id"] == self.order.id for o in response.data))

    def test_orders_list_unauthenticated(self):
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 401)
