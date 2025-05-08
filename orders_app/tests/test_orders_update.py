from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from core.utils.test_client import JSONAPIClient


class OrdersUpdateAPITestCase(APITestCase):
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

    def test_patch_order_status_as_business(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.patch(f"/api/orders/{self.order.id}/", {"status": "completed"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "completed")

    def test_patch_order_status_as_customer_forbidden(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(f"/api/orders/{self.order.id}/", {"status": "completed"})
        self.assertEqual(response.status_code, 403)

    def test_patch_order_invalid_status(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.patch(f"/api/orders/{self.order.id}/", {"status": "invalid"})
        self.assertEqual(response.status_code, 400)

    def test_patch_order_unauthenticated(self):
        response = self.client.patch(f"/api/orders/{self.order.id}/", {"status": "completed"})
        self.assertEqual(response.status_code, 401)

    def test_get_not_allowed_on_detail_view(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.get(f"/api/orders/{self.order.id}/")
        self.assertEqual(response.status_code, 405)
        self.assertIn("GET is not allowed", str(response.data))

    def test_put_not_allowed_on_detail_view(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.put(f"/api/orders/{self.order.id}/", {"status": "completed"})
        self.assertEqual(response.status_code, 405)
        self.assertIn("PUT is not allowed", str(response.data))
