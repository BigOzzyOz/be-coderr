from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from core.utils.test_client import JSONAPIClient
from reviews_app.models import Review


class TestReviewDetailView(APITestCase):
    client_class = JSONAPIClient

    @classmethod
    def setUpTestData(cls):
        cls.owner_customer = User.objects.create_user(username="owner_cust", password="pw1", email="ownercust@test.com")
        cls.owner_customer.profile.type = "customer"
        cls.owner_customer.profile.save()
        cls.other_customer = User.objects.create_user(username="other_cust", password="pw1", email="othercust@test.com")
        cls.other_customer.profile.type = "customer"
        cls.other_customer.profile.save()
        cls.business_reviewed = User.objects.create_user(
            username="biz_reviewed", password="pw1", email="bizrev@test.com"
        )
        cls.business_reviewed.profile.type = "business"
        cls.business_reviewed.profile.save()
        cls.business_other = User.objects.create_user(username="biz_other", password="pw1", email="bizother@test.com")
        cls.business_other.profile.type = "business"
        cls.business_other.profile.save()
        cls.review = Review.objects.create(
            reviewer=cls.owner_customer, business_user=cls.business_reviewed, rating=5, description="My Review"
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
        self.detail_url = reverse("reviews-detail", kwargs={"pk": self.review.pk})
        self.non_existent_url = reverse("reviews-detail", kwargs={"pk": 999})

    def test_get_review_detail_unauthenticated(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_review_detail_authenticated_owner(self):
        self.client.force_authenticate(user=self.owner_customer)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 405)
        self.assertIn("not allowed", str(response.data))

    def test_get_review_detail_authenticated_other_customer(self):
        self.client.force_authenticate(user=self.other_customer)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 405)
        self.assertIn("not allowed", str(response.data))

    def test_get_review_detail_authenticated_business_user(self):
        self.client.force_authenticate(user=self.business_reviewed)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 405)
        self.assertIn("not allowed", str(response.data))

    def test_get_review_detail_non_existent(self):
        self.client.force_authenticate(user=self.owner_customer)
        response = self.client.get(self.non_existent_url)
        self.assertEqual(response.status_code, 405)
        self.assertIn("not allowed", str(response.data))

    def test_patch_review_unauthenticated(self):
        data = {"rating": 1, "description": "Updated badly"}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_review_authenticated_owner_success(self):
        self.client.force_authenticate(user=self.owner_customer)
        data = {"rating": 1, "description": "Updated by owner"}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 1)
        self.assertEqual(self.review.description, "Updated by owner")
        self.assertEqual(response.data["business_user"], self.business_reviewed.id)

    def test_patch_review_authenticated_other_customer_forbidden(self):
        self.client.force_authenticate(user=self.other_customer)
        data = {"rating": 2}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_review_authenticated_business_user_forbidden(self):
        self.client.force_authenticate(user=self.business_reviewed)
        data = {"rating": 2}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_review_owner_try_change_business_user_ignored(self):
        self.client.force_authenticate(user=self.owner_customer)
        original_business_user_id = self.review.business_user.id
        data = {"business_user": self.business_other.id, "rating": 3}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.business_user.id, original_business_user_id)
        self.assertEqual(self.review.rating, 3)

    def test_put_review_explicitly_disallowed_by_viewset(self):
        self.client.force_authenticate(user=self.owner_customer)
        data = {"business_user": self.business_reviewed.id, "rating": 1, "description": "PUT attempt"}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertIn("PUT is not allowed. Use PATCH instead.", response.data.get("detail", ""))

    def test_delete_review_unauthenticated(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_review_authenticated_owner_success(self):
        self.client.force_authenticate(user=self.owner_customer)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())

    def test_delete_review_authenticated_other_customer_forbidden(self):
        self.client.force_authenticate(user=self.other_customer)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_authenticated_business_user_forbidden(self):
        self.client.force_authenticate(user=self.business_reviewed)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_non_existent(self):
        self.client.force_authenticate(user=self.owner_customer)
        response = self.client.delete(self.non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
