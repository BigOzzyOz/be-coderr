from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from reviews_app.models import Review
from offers_app.models import Offer, OfferDetail
from core.utils.test_client import JSONAPIClient


class TestBaseInfoView(APITestCase):
    client_class = JSONAPIClient

    def test_base_info_view_response_fields(self):
        url = reverse("infos_app:base-info")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("review_count", data)
        self.assertIn("average_rating", data)
        self.assertIn("business_profile_count", data)
        self.assertIn("offer_count", data)

    def test_base_info_view_counts(self):
        business = User.objects.create(username="businessuser", email="business@mail.de")
        business.profile.type = "business"
        business.profile.save()

        user_profile = User.objects.create(username="normaluser", email="user@mail.de")
        user_profile.type = "customer"
        user_profile.save()

        user2 = User.objects.create(username="revieweruser", email="reviewer@mail.de")
        user2.type = "customer"
        user2.save()

        Review.objects.create(rating=4, business_user=business, reviewer=user2)
        Review.objects.create(rating=2, business_user=business, reviewer=user_profile)  # anderer reviewer!
        offer = Offer.objects.create(user=business, title="Test", description="desc")
        OfferDetail.objects.create(
            offer=offer,
            title="Detail1",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["A"],
            offer_type="basic",
        )
        url = reverse("infos_app:base-info")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data["review_count"], 2)
        self.assertEqual(data["average_rating"], 3.0)
        self.assertEqual(data["business_profile_count"], 1)
        self.assertEqual(data["offer_count"], 1)
