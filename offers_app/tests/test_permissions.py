from rest_framework.test import APITestCase
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from offers_app.models import Offer
from offers_app.api.permissions import IsAuthenticatedOrBusinessCreateOrOwnerUpdateDelete
from core.utils.test_client import JSONAPIClient


class TestOfferPermissions(APITestCase):
    """Tests for offer permissions (IsAuthenticatedOrBusinessCreateOrOwnerUpdateDelete)."""
    client_class = JSONAPIClient

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.permission = IsAuthenticatedOrBusinessCreateOrOwnerUpdateDelete()
        cls.view = object()

        cls.owner = User.objects.create_user(username="owner", password="pw1", email="owner@test.com")
        cls.non_owner = User.objects.create_user(username="nonowner", password="pw2", email="nonowner@test.com")
        cls.anonymous_user = AnonymousUser()

        cls.offer_owned = Offer.objects.create(user=cls.owner, title="Owned Offer", description="Desc")

    def test_has_object_permission_safe_methods_authenticated(self):
        """Test safe methods allowed for authenticated users."""
        request = self.factory.get("/fake-url/")
        request.user = self.non_owner
        self.assertTrue(self.permission.has_object_permission(request, self.view, self.offer_owned))

    def test_has_object_permission_safe_methods_unauthenticated(self):
        """Test safe methods denied for unauthenticated users."""
        request = self.factory.get("/fake-url/")
        request.user = self.anonymous_user
        self.assertFalse(self.permission.has_object_permission(request, self.view, self.offer_owned))

    def test_has_object_permission_owner_patch(self):
        """Test PATCH allowed for owner."""
        request = self.factory.patch("/fake-url/")
        request.user = self.owner
        self.assertTrue(self.permission.has_object_permission(request, self.view, self.offer_owned))

    def test_has_object_permission_owner_put(self):
        """Test PUT allowed for owner."""
        request = self.factory.put("/fake-url/")
        request.user = self.owner
        self.assertTrue(self.permission.has_object_permission(request, self.view, self.offer_owned))

    def test_has_object_permission_owner_delete(self):
        """Test DELETE allowed for owner."""
        request = self.factory.delete("/fake-url/")
        request.user = self.owner
        self.assertTrue(self.permission.has_object_permission(request, self.view, self.offer_owned))

    def test_has_object_permission_not_owner_patch(self):
        """Test PATCH denied for non-owner."""
        request = self.factory.patch("/fake-url/")
        request.user = self.non_owner
        self.assertFalse(self.permission.has_object_permission(request, self.view, self.offer_owned))

    def test_has_object_permission_not_owner_put(self):
        """Test PUT denied for non-owner."""
        request = self.factory.put("/fake-url/")
        request.user = self.non_owner
        self.assertFalse(self.permission.has_object_permission(request, self.view, self.offer_owned))

    def test_has_object_permission_not_owner_delete(self):
        """Test DELETE denied for non-owner."""
        request = self.factory.delete("/fake-url/")
        request.user = self.non_owner
        self.assertFalse(self.permission.has_object_permission(request, self.view, self.offer_owned))

    def test_has_object_permission_unauthenticated_unsafe(self):
        """Test unsafe methods denied for unauthenticated users."""
        request = self.factory.patch("/fake-url/")
        request.user = self.anonymous_user
        self.assertFalse(self.permission.has_object_permission(request, self.view, self.offer_owned))

    def test_has_permission_post_business(self):
        """Test POST allowed for business user."""
        request = self.factory.post("/fake-url/")
        self.owner.profile.type = "business"
        self.owner.profile.save()
        request.user = self.owner
        self.assertTrue(self.permission.has_permission(request, self.view))

    def test_has_permission_post_non_business(self):
        """Test POST denied for non-business user."""
        request = self.factory.post("/fake-url/")
        self.non_owner.profile.type = "customer"
        self.non_owner.profile.save()
        request.user = self.non_owner
        self.assertFalse(self.permission.has_permission(request, self.view))
