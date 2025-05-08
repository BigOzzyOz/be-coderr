from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from core.utils.test_client import JSONAPIClient
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order


class OrdersPermissionsAPITestCase(APITestCase):
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

    def test_customer_cannot_patch_order(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(f"/api/orders/{self.order.id}/", {"status": "completed"})
        self.assertEqual(response.status_code, 403)

    def test_business_can_patch_order(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.patch(f"/api/orders/{self.order.id}/", {"status": "completed"})
        self.assertEqual(response.status_code, 200)

    def test_only_staff_can_delete_order(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(f"/api/orders/{self.order.id}/")
        self.assertEqual(response.status_code, 403)
        self.client.force_authenticate(user=self.business)
        response = self.client.delete(f"/api/orders/{self.order.id}/")
        self.assertEqual(response.status_code, 403)
        self.client.force_authenticate(user=self.staff)
        response = self.client.delete(f"/api/orders/{self.order.id}/")
        self.assertEqual(response.status_code, 204)

    def test_only_customer_can_create_order(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.post("/api/orders/", {"offer_detail_id": self.offer_detail.id})
        self.assertEqual(response.status_code, 403)
        self.client.force_authenticate(user=self.customer)
        response = self.client.post("/api/orders/", {"offer_detail_id": self.offer_detail.id})
        self.assertEqual(response.status_code, 201)

    def test_object_permission_denied_for_unauthenticated(self):
        from orders_app.api.permissions import IsAuthenticatedOrCustomerCreateOrBusinessUpdateOrStaffDelete

        class DummyObj:
            pass

        class DummyRequest:
            def __init__(self):
                self.user = type("User", (), {"is_authenticated": False})()
                self.method = "GET"

        perm = IsAuthenticatedOrCustomerCreateOrBusinessUpdateOrStaffDelete()
        req = DummyRequest()
        self.assertFalse(perm.has_object_permission(req, None, DummyObj()))

    def test_object_permission_safe_method(self):
        from orders_app.api.permissions import IsAuthenticatedOrCustomerCreateOrBusinessUpdateOrStaffDelete

        class DummyObj:
            pass

        class DummyUser:
            is_authenticated = True
            profile = type("Profile", (), {"type": "customer"})()

        class DummyRequest:
            def __init__(self):
                self.user = DummyUser()
                self.method = "GET"

        perm = IsAuthenticatedOrCustomerCreateOrBusinessUpdateOrStaffDelete()
        req = DummyRequest()
        self.assertTrue(perm.has_object_permission(req, None, DummyObj()))
