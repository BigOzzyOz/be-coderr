from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from core.utils.test_client import JSONAPIClient


class OrdersDeleteAPITestCase(APITestCase):
    """Tests for order deletion API endpoint."""

    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user(username="kunde", password="pass1234", email="kunde@mail.de")
        cls.customer.profile.type = "customer"
        cls.customer.profile.save()
        cls.business = User.objects.create_user(username="business", password="pass1234", email="business@mail.de")
        cls.business.profile.type = "business"
        cls.business.profile.save()
        cls.staff = User.objects.create_user(
            username="admin", password="pass1234", email="admin@mail.de", is_staff=True
        )
        cls.staff.profile.type = "business"
        cls.staff.profile.save()
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

    def test_delete_order_as_staff(self):
        """Test that staff can delete an order."""
        self.client.force_authenticate(user=self.staff)
        response = self.client.delete(f"/api/orders/{self.order.id}/")
        self.assertEqual(response.status_code, 204)

    def test_delete_order_as_customer_forbidden(self):
        """Test that customers cannot delete an order."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(f"/api/orders/{self.order.id}/")
        self.assertEqual(response.status_code, 403)

    def test_delete_order_unauthenticated(self):
        """Test that unauthenticated users cannot delete an order."""
        response = self.client.delete(f"/api/orders/{self.order.id}/")
        self.assertEqual(response.status_code, 401)

    def test_delete_order_not_found(self):
        """Test that deleting a non-existent order returns 404."""
        self.client.force_authenticate(user=self.staff)
        response = self.client.delete("/api/orders/9999/")
        self.assertEqual(response.status_code, 404)
