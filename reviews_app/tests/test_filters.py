from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIRequestFactory
from reviews_app.models import Review
from reviews_app.api.filters import ReviewFilter
from core.utils.test_client import JSONAPIClient


class ReviewFilterTests(APITestCase):
    """Tests for the ReviewFilter class (filtering reviews by user/business)."""

    client_class = JSONAPIClient

    @classmethod
    def setUpTestData(cls):
        cls.customer1 = User.objects.create_user(username="custfilter1", password="pw", email="custfilter1@example.com")
        cls.customer1.profile.type = "customer"
        cls.customer1.profile.save()
        cls.customer2 = User.objects.create_user(username="custfilter2", password="pw", email="custfilter2@example.com")
        cls.customer2.profile.type = "customer"
        cls.customer2.profile.save()
        cls.business1 = User.objects.create_user(username="bizfilter1", password="pw", email="bizfilter1@example.com")
        cls.business1.profile.type = "business"
        cls.business1.profile.save()
        cls.business2 = User.objects.create_user(username="bizfilter2", password="pw", email="bizfilter2@example.com")
        cls.business2.profile.type = "business"
        cls.business2.profile.save()
        cls.review1_c1_b1 = Review.objects.create(reviewer=cls.customer1, business_user=cls.business1, rating=5)
        cls.review2_c1_b2 = Review.objects.create(reviewer=cls.customer1, business_user=cls.business2, rating=4)
        cls.review3_c2_b1 = Review.objects.create(reviewer=cls.customer2, business_user=cls.business1, rating=3)

    def setUp(self):
        super().setUp()
        if not hasattr(self, "factory"):
            try:
                self.factory = APIRequestFactory()
                if not hasattr(self, "client") and hasattr(self, "client_class"):
                    self.client = self.client_class()
            except Exception:
                pass

    def test_filter_by_business_user_id(self):
        """Test filtering reviews by business_user_id returns correct reviews."""
        data = {"business_user_id": self.business1.id}
        qs = Review.objects.all()
        filtered_qs = ReviewFilter(data=data, queryset=qs).qs
        self.assertIn(self.review1_c1_b1, filtered_qs)
        self.assertIn(self.review3_c2_b1, filtered_qs)
        self.assertNotIn(self.review2_c1_b2, filtered_qs)
        self.assertEqual(filtered_qs.count(), 2)

    def test_filter_by_reviewer_id(self):
        """Test filtering reviews by reviewer_id returns correct reviews."""
        data = {"reviewer_id": self.customer1.id}
        qs = Review.objects.all()
        filtered_qs = ReviewFilter(data=data, queryset=qs).qs
        self.assertIn(self.review1_c1_b1, filtered_qs)
        self.assertIn(self.review2_c1_b2, filtered_qs)
        self.assertNotIn(self.review3_c2_b1, filtered_qs)
        self.assertEqual(filtered_qs.count(), 2)

    def test_filter_by_business_user_id_and_reviewer_id(self):
        """Test filtering by both business_user_id and reviewer_id returns correct review."""
        data = {"business_user_id": self.business1.id, "reviewer_id": self.customer1.id}
        qs = Review.objects.all()
        filtered_qs = ReviewFilter(data=data, queryset=qs).qs
        self.assertIn(self.review1_c1_b1, filtered_qs)
        self.assertNotIn(self.review2_c1_b2, filtered_qs)
        self.assertNotIn(self.review3_c2_b1, filtered_qs)
        self.assertEqual(filtered_qs.count(), 1)

    def test_filter_no_match_business_user_id(self):
        """Test filtering with non-existent business_user_id returns no results."""
        non_existent_id = 9999
        data = {"business_user_id": non_existent_id}
        qs = Review.objects.all()
        filtered_qs = ReviewFilter(data=data, queryset=qs).qs
        self.assertEqual(filtered_qs.count(), 0)

    def test_filter_no_match_reviewer_id(self):
        """Test filtering with non-existent reviewer_id returns no results."""
        non_existent_id = 8888
        data = {"reviewer_id": non_existent_id}
        qs = Review.objects.all()
        filtered_qs = ReviewFilter(data=data, queryset=qs).qs
        self.assertEqual(filtered_qs.count(), 0)

    def test_filter_no_params_returns_all(self):
        """Test filtering with no params returns all reviews."""
        data = {}
        qs = Review.objects.all()
        filtered_qs = ReviewFilter(data=data, queryset=qs).qs
        self.assertEqual(filtered_qs.count(), Review.objects.count())
        self.assertEqual(filtered_qs.count(), 3)
