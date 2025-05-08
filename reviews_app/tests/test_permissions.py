from django.contrib.auth.models import User, AnonymousUser
from rest_framework.test import APITestCase, APIRequestFactory
from reviews_app.models import Review
from reviews_app.api.permissions import IsAuthenticatedOrCustomerCreateOrOwnerUpdateDelete
from core.utils.test_client import JSONAPIClient


class TestReviewPermissions(APITestCase):
    """Tests for IsAuthenticatedOrCustomerCreateOrOwnerUpdateDelete permission class."""

    client_class = JSONAPIClient

    @classmethod
    def setUpTestData(cls):
        cls.customer_user1 = User.objects.create_user(username="cust1", password="pw1", email="cust1@example.com")
        cls.customer_user1.profile.type = "customer"
        cls.customer_user1.profile.save()
        cls.customer_user2 = User.objects.create_user(username="cust2", password="pw1", email="cust2@example.com")
        cls.customer_user2.profile.type = "customer"
        cls.customer_user2.profile.save()
        cls.business_user = User.objects.create_user(username="biz", password="pw1", email="biz@example.com")
        cls.business_user.profile.type = "business"
        cls.business_user.profile.save()
        cls.review_by_cust1 = Review.objects.create(
            reviewer=cls.customer_user1, business_user=cls.business_user, rating=5
        )

    def setUp(self):
        super().setUp()
        if not hasattr(self, "factory"):
            try:
                self.factory = APIRequestFactory()
                if not hasattr(self, "client") and hasattr(self, "client_class"):
                    self.client = self.client_class()
            except Exception:
                pass
        self.permission = IsAuthenticatedOrCustomerCreateOrOwnerUpdateDelete()
        self.mock_view = type("MockView", (), {})()

    def test_has_permission_safe_methods_authenticated(self):
        """Test safe methods: authenticated users have permission."""
        request = self.factory.get("/fake-url")
        request.user = self.customer_user1
        self.assertTrue(self.permission.has_permission(request, self.mock_view))
        request.user = self.business_user
        self.assertTrue(self.permission.has_permission(request, self.mock_view))

    def test_has_permission_safe_methods_unauthenticated_false(self):
        """Test safe methods: unauthenticated users have no permission."""
        request = self.factory.get("/fake-url")
        request.user = AnonymousUser()
        self.assertFalse(self.permission.has_permission(request, self.mock_view))

    def test_has_permission_post_customer_true(self):
        """Test POST: customer user has permission."""
        request = self.factory.post("/fake-url")
        request.user = self.customer_user1
        self.assertTrue(self.permission.has_permission(request, self.mock_view))

    def test_has_permission_post_business_false(self):
        """Test POST: business user has no permission."""
        request = self.factory.post("/fake-url")
        request.user = self.business_user
        self.assertFalse(self.permission.has_permission(request, self.mock_view))

    def test_has_permission_post_unauthenticated_false(self):
        """Test POST: unauthenticated user has no permission."""
        request = self.factory.post("/fake-url")
        request.user = AnonymousUser()
        self.assertFalse(self.permission.has_permission(request, self.mock_view))

    def test_has_permission_patch_delete_put_authenticated_true(self):
        """Test PATCH/DELETE/PUT: authenticated users have permission."""
        for method_name in ["patch", "delete", "put"]:
            request = getattr(self.factory, method_name)("/fake-url")
            request.user = self.customer_user1
            self.assertTrue(
                self.permission.has_permission(request, self.mock_view), f"Failed for {method_name} with customer"
            )
            request = getattr(self.factory, method_name)("/fake-url")
            request.user = self.business_user
            self.assertTrue(
                self.permission.has_permission(request, self.mock_view), f"Failed for {method_name} with business"
            )

    def test_has_permission_patch_delete_put_unauthenticated_false(self):
        """Test PATCH/DELETE/PUT: unauthenticated users have no permission."""
        for method_name in ["patch", "delete", "put"]:
            request = getattr(self.factory, method_name)("/fake-url")
            request.user = AnonymousUser()
            self.assertFalse(self.permission.has_permission(request, self.mock_view), f"Failed for {method_name}")

    def test_has_object_permission_safe_methods_authenticated_true(self):
        """Test safe methods: authenticated users have object permission."""
        request = self.factory.get("/fake-url")
        request.user = self.customer_user1
        self.assertTrue(self.permission.has_object_permission(request, self.mock_view, self.review_by_cust1))
        request.user = self.customer_user2
        self.assertTrue(self.permission.has_object_permission(request, self.mock_view, self.review_by_cust1))
        request.user = self.business_user
        self.assertTrue(self.permission.has_object_permission(request, self.mock_view, self.review_by_cust1))

    def test_has_object_permission_safe_methods_unauthenticated_false(self):
        """Test safe methods: unauthenticated users have no object permission."""
        request = self.factory.get("/fake-url")
        request.user = AnonymousUser()
        self.assertFalse(self.permission.has_object_permission(request, self.mock_view, self.review_by_cust1))

    def test_has_object_permission_edit_methods_owner_true(self):
        """Test PATCH/DELETE/PUT: owner has object permission."""
        for method_name in ["patch", "delete", "put"]:
            request = getattr(self.factory, method_name)("/fake-url")
            request.user = self.customer_user1
            self.assertTrue(
                self.permission.has_object_permission(request, self.mock_view, self.review_by_cust1),
                f"Failed for {method_name}",
            )

    def test_has_object_permission_edit_methods_not_owner_false(self):
        """Test PATCH/DELETE/PUT: non-owner has no object permission."""
        for method_name in ["patch", "delete", "put"]:
            request = getattr(self.factory, method_name)("/fake-url")
            request.user = self.customer_user2
            self.assertFalse(
                self.permission.has_object_permission(request, self.mock_view, self.review_by_cust1),
                f"Failed for {method_name} with other customer",
            )
            request = getattr(self.factory, method_name)("/fake-url")
            request.user = self.business_user
            self.assertFalse(
                self.permission.has_object_permission(request, self.mock_view, self.review_by_cust1),
                f"Failed for {method_name} with business user",
            )

    def test_has_object_permission_edit_methods_unauthenticated_false(self):
        """Test PATCH/DELETE/PUT: unauthenticated user has no object permission."""
        for method_name in ["patch", "delete", "put"]:
            request = getattr(self.factory, method_name)("/fake-url")
            request.user = AnonymousUser()
            self.assertFalse(
                self.permission.has_object_permission(request, self.mock_view, self.review_by_cust1),
                f"Failed for {method_name}",
            )
