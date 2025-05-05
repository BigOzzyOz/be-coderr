from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from core.utils.test_client import JSONAPIClient
from profiles_app.api.views import CustomerProfileListView, BusinessProfileListView


class TestProfileListViews(APITestCase):
    client_class = JSONAPIClient

    def setUp(self):
        self.user = User.objects.create_user(username="customer1", password="pw123", email="c1@mail.de")
        self.profile = self.user.profile
        self.profile.type = "customer"
        self.profile.save()
        self.business_user = User.objects.create_user(username="business1", password="pw123", email="b1@mail.de")
        self.business_profile = self.business_user.profile
        self.business_profile.type = "business"
        self.business_profile.save()
        self.customer_url = reverse("customer-profiles")
        self.business_url = reverse("business-profiles")

    def test_customer_list_unauthenticated(self):
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)

    def test_customer_list_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(p["user"] == self.user.pk for p in response.data))

    def test_customer_list_internal_server_error(self):
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
        response = self.client.get(self.business_url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)

    def test_business_list_success(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get(self.business_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(p["user"] == self.business_user.pk for p in response.data))

    def test_business_list_internal_server_error(self):
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
