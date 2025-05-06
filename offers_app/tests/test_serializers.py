from decimal import Decimal
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from django.contrib.auth.models import User
from offers_app.models import Offer, OfferDetail
from offers_app.api.serializers import OfferSerializer
from rest_framework.exceptions import ValidationError
from unittest.mock import patch
from core.utils.test_client import JSONAPIClient


class OfferSerializerTests(APITestCase):
    client_class = JSONAPIClient

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="pw1", email="test@test.com")
        cls.offer_with_details = Offer.objects.create(user=cls.user, title="Offer 1", description="Desc 1")
        cls.detail1 = OfferDetail.objects.create(
            offer=cls.offer_with_details, title="Detail 1.1", price=100, delivery_time_in_days=5
        )
        cls.detail2 = OfferDetail.objects.create(
            offer=cls.offer_with_details, title="Detail 1.2", price=50, delivery_time_in_days=3
        )
        cls.offer_no_details = Offer.objects.create(user=cls.user, title="Offer 2", description="Desc 2")

    def setUp(self):
        super().setUp()

        if not hasattr(self, "factory"):
            try:
                self.factory = APIRequestFactory()
                if not hasattr(self, "client") and hasattr(self, "client_class"):
                    self.client = self.client_class()
            except Exception:
                pass

    def _get_serializer_context(self, method="GET", data=None):
        if method.lower() in ["post", "put", "patch"]:
            request = getattr(self.factory, method.lower())("/fake-url", data=data, format="json")
        else:
            request = getattr(self.factory, method.lower())("/fake-url")
        request.user = self.user
        drf_request = Request(request, parsers=[JSONParser()])
        return {"request": drf_request}

    def test_validate_details_not_a_list(self):
        data = {"title": "Invalid Details Offer", "description": "Test", "details": {"not": "a list"}}
        context = self._get_serializer_context(method="POST", data=data)
        serializer = OfferSerializer(data=data, context=context)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn('Expected a list of items but got type "dict".', str(cm.exception.detail["details"]))

    def test_validate_details_missing_required_field(self):
        data = {
            "title": "Missing Field Offer",
            "description": "Test",
            "details": [
                {"title": "Valid Detail", "price": 10, "delivery_time_in_days": 1},
                {"title": "Missing Price", "delivery_time_in_days": 2},
            ],
        }
        context = self._get_serializer_context(method="POST", data=data)
        serializer = OfferSerializer(data=data, context=context)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("This field is required.", str(cm.exception.detail["details"][1]["price"]))

    def test_get_min_price_no_details(self):
        context = self._get_serializer_context()
        serializer = OfferSerializer(instance=self.offer_no_details, context=context)
        self.assertIsNone(serializer.data["min_price"])

    def test_get_min_delivery_time_no_details(self):
        context = self._get_serializer_context()
        serializer = OfferSerializer(instance=self.offer_no_details, context=context)
        self.assertIsNone(serializer.data["min_delivery_time"])

    def test_update_add_new_details(self):
        data = {
            "details": [
                {"id": self.detail1.id, "price": 110},
                {
                    "title": "New Detail",
                    "price": 200,
                    "delivery_time_in_days": 7,
                    "revisions": 0,
                    "features": ["Feature X", "Feature Y"],
                    "offer_type": "premium",
                },
            ]
        }
        context = self._get_serializer_context(method="PATCH", data=data)
        initial_detail_count = self.offer_with_details.details.count()

        serializer = OfferSerializer(instance=self.offer_with_details, data=data, partial=True, context=context)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        updated_offer = serializer.save()
        self.assertEqual(updated_offer.details.count(), initial_detail_count + 1)
        new_detail = updated_offer.details.latest("id")
        self.assertEqual(new_detail.title, "New Detail")
        self.assertEqual(new_detail.price, Decimal("200.00"))
        self.assertEqual(new_detail.delivery_time_in_days, 7)
        self.assertEqual(new_detail.revisions, 0)
        self.assertEqual(new_detail.features, ["Feature X", "Feature Y"])
        self.assertEqual(new_detail.offer_type, "premium")

        self.detail1.refresh_from_db()
        self.assertEqual(self.detail1.price, Decimal("110.00"))

    def test_validate_details_not_a_list_in_patch(self):
        data = {"details": {"not": "a list"}}
        context = self._get_serializer_context(method="PATCH", data=data)
        serializer = OfferSerializer(instance=self.offer_with_details, data=data, partial=True, context=context)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn('Expected a list of items but got type "dict".', str(cm.exception.detail.get("details")))

    def test_update_nonexistent_detail_id(self):
        non_existent_id = 99999
        data = {
            "details": [
                {"id": non_existent_id, "price": 150},
                {"id": self.detail1.id, "price": 120},
            ]
        }
        context = self._get_serializer_context(method="PATCH", data=data)
        serializer = OfferSerializer(instance=self.offer_with_details, data=data, partial=True, context=context)

        self.assertTrue(serializer.is_valid(raise_exception=True))
        updated_offer = serializer.save()

        self.detail1.refresh_from_db()
        self.assertEqual(self.detail1.price, Decimal("120.00"))
        self.assertEqual(updated_offer.details.count(), 2)

    @patch("offers_app.api.serializers.OfferDetail.objects.create")
    def test_update_create_detail_fails_exception(self, mock_create):
        mock_create.side_effect = Exception("Database connection lost")

        data = {
            "details": [
                {
                    "title": "New Detail Fail",
                    "price": 300,
                    "delivery_time_in_days": 10,
                    "revisions": 1,
                    "offer_type": "basic",
                }
            ]
        }
        context = self._get_serializer_context(method="PATCH", data=data)
        serializer = OfferSerializer(instance=self.offer_with_details, data=data, partial=True, context=context)

        self.assertTrue(serializer.is_valid(raise_exception=True))

        with self.assertRaises(ValidationError) as cm:
            serializer.save()

        self.assertIn("Failed to create a detail: Database connection lost", str(cm.exception))

        mock_create.assert_called_once()

    def test_model_str_methods(self):
        self.assertEqual(str(self.offer_with_details), "Offer by testuser for Offer 1")
        self.assertEqual(str(self.detail1), "Detail 1.1")
        self.assertEqual(str(self.offer_no_details), "Offer by testuser for Offer 2")
