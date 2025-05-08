from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from core.utils.test_client import JSONAPIClient
from offers_app.models import Offer, OfferDetail


class TestOfferCreateView(APITestCase):
    """Tests for offer creation API endpoints."""

    client_class = JSONAPIClient

    @classmethod
    def setUpTestData(cls):
        cls.business_user = User.objects.create_user(username="business", password="pw123", email="b@mail.de")
        cls.business_user.profile.type = "business"
        cls.business_user.profile.save()
        cls.customer_user = User.objects.create_user(username="customer", password="pw123", email="c@mail.de")
        cls.customer_user.profile.type = "customer"
        cls.customer_user.profile.save()
        cls.url = reverse("offer-list")
        cls.valid_data = {
            "title": "Neues Angebot",
            "description": "Beschreibung",
            "details": [
                {
                    "title": "Detail",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["A"],
                    "offer_type": "basic",
                }
            ],
        }

    def setUp(self):
        self.client = self.client_class()

    def test_post_offer_unauthenticated(self):
        """Test that unauthenticated users cannot create offers."""
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 401)

    def test_post_offer_not_business(self):
        """Test that only business users can create offers."""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 403)

    def test_post_offer_success(self):
        """Test successful offer creation with valid data."""
        self.client.force_authenticate(user=self.business_user)
        valid_data = {
            "title": "Neues Angebot",
            "description": "Beschreibung",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["A"],
                    "offer_type": "basic",
                },
                {
                    "title": "Standard",
                    "revisions": 2,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["B"],
                    "offer_type": "standard",
                },
                {
                    "title": "Premium",
                    "revisions": 3,
                    "delivery_time_in_days": 10,
                    "price": 300,
                    "features": ["C"],
                    "offer_type": "premium",
                },
            ],
        }
        response = self.client.post(self.url, valid_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.data)

    def test_post_offer_invalid_data(self):
        """Test offer creation fails with invalid data."""
        self.client.force_authenticate(user=self.business_user)
        data = {"title": "", "details": []}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)

    def test_post_offer_internal_server_error(self):
        """Test server error during offer creation returns 500."""
        self.client.force_authenticate(user=self.business_user)
        valid_data = {
            "title": "Neues Angebot",
            "description": "Beschreibung",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["A"],
                    "offer_type": "basic",
                },
                {
                    "title": "Standard",
                    "revisions": 2,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["B"],
                    "offer_type": "standard",
                },
                {
                    "title": "Premium",
                    "revisions": 3,
                    "delivery_time_in_days": 10,
                    "price": 300,
                    "features": ["C"],
                    "offer_type": "premium",
                },
            ],
        }
        orig_create = Offer.objects.create
        Offer.objects.create = lambda *a, **kw: (_ for _ in ()).throw(Exception("Test-Fehler"))
        try:
            response = self.client.post(self.url, valid_data)
            self.assertEqual(response.status_code, 500)
        finally:
            Offer.objects.create = orig_create

    def test_post_offer_requires_three_types(self):
        """Test that exactly 3 offer details with unique types are required."""
        self.client.force_authenticate(user=self.business_user)
        data = {
            "title": "Test",
            "description": "desc",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 1,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["A"],
                    "offer_type": "basic",
                },
                {
                    "title": "Standard",
                    "revisions": 2,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["B"],
                    "offer_type": "standard",
                },
            ],
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("details", response.data)
        # Falsche Typen
        data["details"].append(
            {
                "title": "Basic2",
                "revisions": 1,
                "delivery_time_in_days": 5,
                "price": 100,
                "features": ["A"],
                "offer_type": "basic",
            }
        )
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("details", response.data)
        data["details"] = [
            {
                "title": "Basic",
                "revisions": 1,
                "delivery_time_in_days": 5,
                "price": 100,
                "features": ["A"],
                "offer_type": "basic",
            },
            {
                "title": "Standard",
                "revisions": 2,
                "delivery_time_in_days": 7,
                "price": 200,
                "features": ["B"],
                "offer_type": "standard",
            },
            {
                "title": "Premium",
                "revisions": 3,
                "delivery_time_in_days": 10,
                "price": 300,
                "features": ["C"],
                "offer_type": "premium",
            },
        ]
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 201)

    def test_patch_offer_detail_type_overwrites(self):
        """Test that PATCH updates only existing offer details by type."""
        self.client.force_authenticate(user=self.business_user)
        offer = Offer.objects.create(user=self.business_user, title="Test", description="desc")
        OfferDetail.objects.create(
            offer=offer,
            title="Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["A"],
            offer_type="basic",
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Standard",
            revisions=2,
            delivery_time_in_days=7,
            price=200,
            features=["B"],
            offer_type="standard",
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Premium",
            revisions=3,
            delivery_time_in_days=10,
            price=300,
            features=["C"],
            offer_type="premium",
        )
        url = reverse("offer-detail", kwargs={"pk": offer.id})
        patch_data = {
            "details": [
                {
                    "title": "Basic Updated",
                    "revisions": 9,
                    "delivery_time_in_days": 99,
                    "price": 999,
                    "features": ["X"],
                    "offer_type": "basic",
                }
            ]
        }
        response = self.client.patch(url, patch_data)
        self.assertEqual(response.status_code, 200)
        offer.refresh_from_db()
        basic = offer.details.get(offer_type="basic")
        self.assertEqual(basic.title, "Basic Updated")
        self.assertEqual(basic.revisions, 9)
        self.assertEqual(basic.delivery_time_in_days, 99)
        self.assertEqual(basic.price, 999)
        self.assertEqual(basic.features, ["X"])
        self.assertEqual(offer.details.filter(offer_type="standard").count(), 1)
        self.assertEqual(offer.details.filter(offer_type="premium").count(), 1)
