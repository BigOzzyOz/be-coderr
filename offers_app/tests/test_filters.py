from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from core.utils.test_client import JSONAPIClient
from offers_app.models import Offer
from offers_app.api.filters import OfferFilter


class OfferFilterTests(APITestCase):
    client_class = JSONAPIClient

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username="user1", password="pw1", email="user1@test.com")
        cls.user2 = User.objects.create_user(username="user2", password="pw2", email="user2@test.com")

        cls.offer1 = Offer.objects.create(
            user=cls.user1, title="Amazing Web Design", description="Professional website creation service."
        )
        cls.offer2 = Offer.objects.create(
            user=cls.user1, title="Logo Creation Expert", description="Unique and modern logo designs."
        )
        cls.offer3 = Offer.objects.create(
            user=cls.user2, title="Data Entry Services", description="Fast and accurate data processing."
        )
        cls.offer4 = Offer.objects.create(
            user=cls.user2, title="Python Web Development", description="Building web apps with Django and Flask."
        )

    def test_filter_search_single_term_title(self):
        data = {"search": "Web"}
        qs = Offer.objects.all()
        filtered_qs = OfferFilter(data=data, queryset=qs).qs
        self.assertIn(self.offer1, filtered_qs)
        self.assertIn(self.offer4, filtered_qs)
        self.assertNotIn(self.offer2, filtered_qs)
        self.assertNotIn(self.offer3, filtered_qs)
        self.assertEqual(filtered_qs.count(), 2)

    def test_filter_search_single_term_description(self):
        data = {"search": "service"}
        qs = Offer.objects.all()
        filtered_qs = OfferFilter(data=data, queryset=qs).qs
        self.assertIn(self.offer1, filtered_qs)
        self.assertIn(self.offer3, filtered_qs)
        self.assertNotIn(self.offer2, filtered_qs)
        self.assertNotIn(self.offer4, filtered_qs)
        self.assertEqual(filtered_qs.count(), 2)

    def test_filter_search_multiple_terms_or(self):
        data = {"search": "Logo Python"}
        qs = Offer.objects.all()
        filtered_qs = OfferFilter(data=data, queryset=qs).qs
        self.assertIn(self.offer2, filtered_qs)
        self.assertIn(self.offer4, filtered_qs)
        self.assertNotIn(self.offer1, filtered_qs)
        self.assertNotIn(self.offer3, filtered_qs)
        self.assertEqual(filtered_qs.count(), 2)

    def test_filter_search_case_insensitive(self):
        data = {"search": "amazing expert"}
        qs = Offer.objects.all()
        filtered_qs = OfferFilter(data=data, queryset=qs).qs
        self.assertIn(self.offer1, filtered_qs)
        self.assertIn(self.offer2, filtered_qs)
        self.assertNotIn(self.offer3, filtered_qs)
        self.assertNotIn(self.offer4, filtered_qs)
        self.assertEqual(filtered_qs.count(), 2)

    def test_filter_search_no_match(self):
        data = {"search": "nonexistentterm"}
        qs = Offer.objects.all()
        filtered_qs = OfferFilter(data=data, queryset=qs).qs
        self.assertEqual(filtered_qs.count(), 0)

    def test_filter_search_partial_match(self):
        data = {"search": "prof data"}
        qs = Offer.objects.all()
        filtered_qs = OfferFilter(data=data, queryset=qs).qs
        self.assertIn(self.offer1, filtered_qs)
        self.assertIn(self.offer3, filtered_qs)
        self.assertNotIn(self.offer2, filtered_qs)
        self.assertNotIn(self.offer4, filtered_qs)
        self.assertEqual(filtered_qs.count(), 2)

    def test_filter_search_empty_string(self):
        data = {"search": ""}
        qs = Offer.objects.all()
        filtered_qs = OfferFilter(data=data, queryset=qs).qs
        self.assertEqual(filtered_qs.count(), 4)

    def test_filter_search_spaces_only(self):
        data = {"search": "   "}
        qs = Offer.objects.all()
        filtered_qs = OfferFilter(data=data, queryset=qs).qs
        self.assertEqual(filtered_qs.count(), 4)
