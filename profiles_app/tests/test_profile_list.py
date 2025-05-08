from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from core.utils.test_client import JSONAPIClient
from profiles_app.api.views import CustomerProfileListView, BusinessProfileListView


class TestProfileListViews(APITestCase):
    """Tests for customer and business profile list API endpoints."""
    client_class = JSONAPIClient

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="customer1", password="pw123", email="c1@mail.de")
        cls.profile = cls.user.profile
        cls.profile.type = "customer"
        cls.profile.save()
        cls.business_user = User.objects.create_user(username="business1", password="pw123", email="b1@mail.de")
        cls.business_profile = cls.business_user.profile
        cls.business_profile.type = "business"
        cls.business_profile.save()
        cls.customer_url = reverse("customer-profiles")
        cls.business_url = reverse("business-profiles")

    def setUp(self):
        self.client = self.client_class()

    def test_customer_list_unauthenticated(self):
        """Test that unauthenticated users cannot list customer profiles."""
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)

    def test_customer_list_success(self):
        """Test that authenticated users can list customer profiles."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(p["user"] == self.user.pk for p in response.data))

    def test_customer_list_internal_server_error(self):
        """Test that internal server error returns 500 for customer list."""
        self.client.force_authenticate(user=self.user)
        orig_get_queryset = CustomerProfileListView.get_queryset

        def error_get_queryset(self):
            raise Exception("Test-Fehler")

        CustomerProfileListView.get_queryset = error_get_queryset
        try:
            response = self.client.get(self.customer_url)
            self.assertEqual(response.status_code, 500)
            self.assertIn("detail", response.data)
        finally:
            CustomerProfileListView.get_queryset = orig_get_queryset

    def test_business_list_unauthenticated(self):
        """Test that unauthenticated users cannot list business profiles."""
        response = self.client.get(self.business_url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)

    def test_business_list_success(self):
        """Test that authenticated users can list business profiles."""
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get(self.business_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(p["user"] == self.business_user.pk for p in response.data))

    def test_business_list_internal_server_error(self):
        """Test that internal server error returns 500 for business list."""
        self.client.force_authenticate(user=self.business_user)
        orig_get_queryset = BusinessProfileListView.get_queryset

        def error_get_queryset(self):
            raise Exception("Test-Fehler")

        BusinessProfileListView.get_queryset = error_get_queryset
        try:
            self.client.raise_request_exception = False
            response = self.client.get(self.business_url)
            self.assertEqual(response.status_code, 500)
            self.assertIn("detail", response.data)
        finally:
            BusinessProfileListView.get_queryset = orig_get_queryset
