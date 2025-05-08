from django.test import TestCase
from django.contrib.auth.models import User
from reviews_app.models import Review
from reviews_app.admin import ReviewAdmin


class ReviewAdminModelTests(TestCase):
    """Tests for ReviewAdmin methods and Review __str__ method."""

    def setUp(self):
        self.reviewer = User.objects.create_user(username="reviewer", password="pw", email="reviewer@test.com")
        self.business = User.objects.create_user(username="business", password="pw", email="business@test.com")
        self.review = Review.objects.create(
            reviewer=self.reviewer, business_user=self.business, rating=5, description="Test"
        )

    def test_reviewer_username_admin(self):
        """Test that reviewer_username returns the correct username."""
        admin = ReviewAdmin(Review, None)
        self.assertEqual(admin.reviewer_username(self.review), "reviewer")

    def test_business_username_admin(self):
        """Test that business_username returns the correct username."""
        admin = ReviewAdmin(Review, None)
        self.assertEqual(admin.business_username(self.review), "business")

    def test_review_str(self):
        """Test the __str__ method of Review returns expected string."""
        self.assertEqual(str(self.review), "Review by reviewer for business")
