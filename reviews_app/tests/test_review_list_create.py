from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from core.utils.test_client import JSONAPIClient
from reviews_app.models import Review


class TestReviewListCreateView(APITestCase):
    client_class = JSONAPIClient

    @classmethod
    def setUpTestData(cls):
        cls.customer_user = User.objects.create_user(username="customer", password="pw1", email="customer@test.com")
        cls.customer_user.profile.type = "customer"
        cls.customer_user.profile.save()
        cls.business_user1 = User.objects.create_user(username="business1", password="pw1", email="business1@test.com")
        cls.business_user1.profile.type = "business"
        cls.business_user1.profile.save()
        cls.business_user2 = User.objects.create_user(username="business2", password="pw2", email="business2@test.com")
        cls.business_user2.profile.type = "business"
        cls.business_user2.profile.save()
        import time

        cls.review1 = Review.objects.create(
            reviewer=cls.customer_user, business_user=cls.business_user1, rating=5, description="Great!"
        )
        time.sleep(0.01)
        cls.review2 = Review.objects.create(
            reviewer=cls.customer_user, business_user=cls.business_user2, rating=4, description="Good."
        )
        cls.list_create_url = reverse("reviews-list")

    def setUp(self):
        super().setUp()
        if not hasattr(self, "factory"):
            try:
                self.factory = APIRequestFactory()
                if not hasattr(self, "client") and hasattr(self, "client_class"):
                    self.client = self.client_class()
            except Exception:
                pass

    def test_get_review_list_unauthenticated(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_review_list_authenticated_customer(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_review_list_authenticated_business(self):
        self.client.force_authenticate(user=self.business_user1)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_review_list_default_ordering(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["id"], self.review2.id)
        self.assertEqual(response.data[1]["id"], self.review1.id)

    def test_get_review_list_ordering_by_rating_asc(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.list_create_url + "?ordering=rating")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["id"], self.review2.id)
        self.assertEqual(response.data[1]["id"], self.review1.id)

    def test_get_review_list_ordering_by_rating_desc(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.list_create_url + "?ordering=-rating")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["id"], self.review1.id)
        self.assertEqual(response.data[1]["id"], self.review2.id)

    def test_create_review_unauthenticated(self):
        data = {"business_user": self.business_user1.id, "rating": 3, "description": "Okay"}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_authenticated_customer_success(self):
        self.client.force_authenticate(user=self.customer_user)
        business_user_for_new_review = User.objects.create_user(username="newbiz", password="pw")
        business_user_for_new_review.profile.type = "business"
        business_user_for_new_review.profile.save()
        data = {"business_user": business_user_for_new_review.id, "rating": 3, "description": "Okay service."}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 3)
        new_review = Review.objects.latest("created_at")
        self.assertEqual(new_review.reviewer, self.customer_user)
        self.assertEqual(new_review.business_user, business_user_for_new_review)
        self.assertEqual(new_review.rating, 3)

    def test_create_review_authenticated_business_user_forbidden(self):
        self.client.force_authenticate(user=self.business_user1)
        data = {"business_user": self.business_user2.id, "rating": 1, "description": "Bad."}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_review_customer_reviews_themselves_fail(self):
        self.client.force_authenticate(user=self.customer_user)
        data = {"business_user": self.customer_user.id, "rating": 5, "description": "I am great!"}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Users cannot review themselves.", str(response.data))

    def test_create_review_customer_already_reviewed_fail(self):
        self.client.force_authenticate(user=self.customer_user)
        data = {"business_user": self.business_user1.id, "rating": 1, "description": "Trying again."}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You have already reviewed this business.", str(response.data.get("non_field_errors", "")))

    def test_create_review_missing_rating(self):
        self.client.force_authenticate(user=self.customer_user)
        temp_business_user = User.objects.create_user(username="tempbiz_norating", password="pw")
        temp_business_user.profile.type = "business"
        temp_business_user.profile.save()
        data = {"business_user": temp_business_user.id, "description": "No rating."}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating", response.data)

    def test_create_review_invalid_rating_too_high(self):
        self.client.force_authenticate(user=self.customer_user)
        temp_business_user = User.objects.create_user(username="tempbiz_highrating", password="pw")
        temp_business_user.profile.type = "business"
        temp_business_user.profile.save()
        data = {"business_user": temp_business_user.id, "rating": 6, "description": "Too high."}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating", response.data)

    def test_create_review_invalid_rating_too_low(self):
        self.client.force_authenticate(user=self.customer_user)
        temp_business_user = User.objects.create_user(username="tempbiz_lowrating", password="pw")
        temp_business_user.profile.type = "business"
        temp_business_user.profile.save()
        data = {"business_user": temp_business_user.id, "rating": 0, "description": "Too low."}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating", response.data)
