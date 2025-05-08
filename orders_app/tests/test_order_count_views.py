from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from core.utils.test_client import JSONAPIClient


class OrderCountViewsAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user(username="customer", password="pass1234", email="kunde@mail.de")
        cls.customer.profile.type = "customer"
        cls.customer.profile.save()
        cls.business = User.objects.create_user(username="business", password="pass1234", email="business@mail.de")
        cls.business.profile.type = "business"
        cls.business.profile.save()
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
        cls.order1 = Order.objects.create(
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
        cls.order2 = Order.objects.create(
            customer_user=cls.customer,
            business_user=cls.business,
            title=cls.offer_detail.title,
            revisions=cls.offer_detail.revisions,
            delivery_time_in_days=cls.offer_detail.delivery_time_in_days,
            price=cls.offer_detail.price,
            features=cls.offer_detail.features,
            offer_type=cls.offer_detail.offer_type,
            status="completed",
        )

    def setUp(self):
        self.client = JSONAPIClient()

    def test_order_count_view(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f"/api/order-count/{self.business.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["order_count"], 2)

    def test_completed_order_count_view(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f"/api/completed-order-count/{self.business.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["completed_order_count"], 1)

    def test_order_count_view_not_found(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get("/api/order-count/9999/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["order_count"], 0)

    def test_completed_order_count_view_not_found(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get("/api/completed-order-count/9999/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["completed_order_count"], 0)
