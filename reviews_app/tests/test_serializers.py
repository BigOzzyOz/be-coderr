from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ValidationError
from reviews_app.models import Review
from reviews_app.api.serializers import ReviewSerializer
from unittest.mock import patch
from core.utils.test_client import JSONAPIClient


class ReviewSerializerTests(APITestCase):
    client_class = JSONAPIClient

    @classmethod
    def setUpTestData(cls):
        cls.reviewer_user = User.objects.create_user(username="reviewer", password="pw1", email="reviewer@test.com")
        cls.reviewer_user.profile.type = "customer"
        cls.reviewer_user.profile.save()

        cls.business_user = User.objects.create_user(username="business", password="pw1", email="business@test.com")
        cls.business_user.profile.type = "business"
        cls.business_user.profile.save()

        cls.other_business_user = User.objects.create_user(
            username="otherbiz", password="pw1", email="otherbiz@test.com"
        )
        cls.other_business_user.profile.type = "business"
        cls.other_business_user.profile.save()

        cls.existing_review = Review.objects.create(
            reviewer=cls.reviewer_user, business_user=cls.business_user, rating=4, description="Good stuff"
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

    def _get_serializer_context(self, user, method="GET", data=None):
        if method.lower() in ["post", "put", "patch"]:
            request_obj = getattr(self.factory, method.lower())("/fake-url", data=data, format="json")
        else:
            request_obj = getattr(self.factory, method.lower())("/fake-url")
        request_obj.user = user
        drf_request = Request(request_obj, parsers=[JSONParser()])
        drf_request.user = user
        return {"request": drf_request}

    def test_serialize_review_instance(self):
        context = self._get_serializer_context(self.reviewer_user)
        serializer = ReviewSerializer(instance=self.existing_review, context=context)
        data = serializer.data
        self.assertEqual(data["id"], self.existing_review.id)
        self.assertEqual(data["reviewer"], self.reviewer_user.id)
        self.assertEqual(data["business_user"], self.business_user.id)
        self.assertEqual(data["business_user_username"], self.business_user.username)
        self.assertEqual(data["rating"], 4)
        self.assertEqual(data["description"], "Good stuff")

    def test_create_review_valid_data(self):
        context = self._get_serializer_context(self.reviewer_user, method="POST")
        data = {"business_user": self.other_business_user.id, "rating": 5, "description": "Excellent!"}
        serializer = ReviewSerializer(data=data, context=context)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        review = serializer.save()
        self.assertEqual(review.reviewer, self.reviewer_user)
        self.assertEqual(review.business_user, self.other_business_user)
        self.assertEqual(review.rating, 5)

    def test_create_review_reviewer_is_business_user_fail(self):
        context = self._get_serializer_context(self.reviewer_user, method="POST")
        data = {"business_user": self.reviewer_user.id, "rating": 3, "description": "Self review"}
        serializer = ReviewSerializer(data=data, context=context)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Users cannot review themselves.", str(cm.exception.detail.get("non_field_errors", "")))

    def test_create_review_already_exists_fail(self):
        context = self._get_serializer_context(self.reviewer_user, method="POST")
        data = {"business_user": self.business_user.id, "rating": 1, "description": "Another try"}
        serializer = ReviewSerializer(data=data, context=context)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("You have already reviewed this business.", str(cm.exception.detail.get("non_field_errors", "")))

    def test_update_review_valid_data(self):
        context = self._get_serializer_context(self.reviewer_user, method="PATCH")
        data = {"rating": 2, "description": "Updated description"}
        serializer = ReviewSerializer(instance=self.existing_review, data=data, partial=True, context=context)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        review = serializer.save()
        self.assertEqual(review.rating, 2)
        self.assertEqual(review.description, "Updated description")

    def test_update_review_try_change_business_user_ignored(self):
        context = self._get_serializer_context(self.reviewer_user, method="PATCH")
        original_business_user = self.existing_review.business_user
        data = {"business_user": self.other_business_user.id, "rating": 1}
        serializer = ReviewSerializer(instance=self.existing_review, data=data, partial=True, context=context)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        review = serializer.save()
        self.assertEqual(review.business_user, original_business_user)
        self.assertEqual(review.rating, 1)

    def test_update_review_try_change_reviewer_ignored(self):
        context = self._get_serializer_context(self.reviewer_user, method="PATCH")
        original_reviewer = self.existing_review.reviewer
        dummy_user = User.objects.create_user(username="dummy", password="pw")
        dummy_user.profile.type = "customer"
        dummy_user.profile.save()

        data = {"reviewer": dummy_user.id, "rating": 1}
        serializer = ReviewSerializer(instance=self.existing_review, data=data, partial=True, context=context)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        review = serializer.save()
        self.assertEqual(review.reviewer, original_reviewer)
        self.assertEqual(review.rating, 1)

    def test_validate_missing_request_context(self):
        data = {"business_user": self.business_user.id, "rating": 5, "description": "desc"}
        serializer = ReviewSerializer(data=data)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        detail = cm.exception.detail
        if isinstance(detail, dict):
            error_text = str(detail.get("non_field_errors", "")) + str(detail)
        elif isinstance(detail, list):
            error_text = " ".join(str(x) for x in detail)
        else:
            error_text = str(detail)
        self.assertIn("Request context is missing", error_text)

    def test_validate_missing_user_in_request_context(self):
        factory = APIRequestFactory()
        request_obj = factory.get("/fake-url")
        drf_request = Request(request_obj, parsers=[JSONParser()])
        context = {"request": drf_request}
        data = {"business_user": self.business_user.id, "rating": 5, "description": "desc"}
        serializer = ReviewSerializer(data=data, context=context)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        detail = cm.exception.detail
        if isinstance(detail, dict):
            error_text = str(detail.get("non_field_errors", "")) + str(detail)
        elif isinstance(detail, list):
            error_text = " ".join(str(x) for x in detail)
        else:
            error_text = str(detail)
        self.assertIn("user is not available", error_text)

    def test_validate_fallback_to_request__request_user(self):
        context = self._get_serializer_context(self.reviewer_user, method="POST")
        drf_request = context["request"]
        drf_request.user = None
        drf_request._request.user = self.reviewer_user
        data = {"business_user": self.other_business_user.id, "rating": 5, "description": "Fallback!"}
        serializer = ReviewSerializer(data=data, context={"request": drf_request})
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_validate_user_not_authenticated(self):
        class DummyUser:
            is_authenticated = False

        context = self._get_serializer_context(self.reviewer_user, method="POST")
        drf_request = context["request"]
        drf_request.user = DummyUser()
        data = {"business_user": self.other_business_user.id, "rating": 5, "description": "Not auth!"}
        serializer = ReviewSerializer(data=data, context={"request": drf_request})
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("user is not available", str(cm.exception.detail.get("non_field_errors", "")))

    def test_validate_users_cannot_review_themselves(self):
        context = self._get_serializer_context(self.reviewer_user, method="POST")
        data = {"business_user": self.reviewer_user.id, "rating": 5, "description": "Self review!"}
        serializer = ReviewSerializer(data=data, context=context)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Users cannot review themselves.", str(cm.exception.detail.get("non_field_errors", "")))

    def test_validate_duplicate_review(self):
        context = self._get_serializer_context(self.reviewer_user, method="POST")
        data = {"business_user": self.business_user.id, "rating": 5, "description": "Duplicate!"}
        serializer = ReviewSerializer(data=data, context=context)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("You have already reviewed this business.", str(cm.exception.detail.get("non_field_errors", "")))

    def test_create_integrity_error(self):
        context = self._get_serializer_context(self.reviewer_user, method="POST")
        data = {"business_user": self.other_business_user.id, "rating": 5, "description": "Integrity!"}
        serializer = ReviewSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        orig_create = Review.objects.create

        def raise_integrity(*a, **kw):
            from django.db import IntegrityError

            raise IntegrityError()

        Review.objects.create = raise_integrity
        try:
            with self.assertRaises(ValidationError) as cm:
                serializer.save()
            self.assertIn("This review already exists.", str(cm.exception.detail.get("non_field_errors", "")))
        finally:
            Review.objects.create = orig_create

    def test_validate_duplicate_review_exists_query(self):
        context = self._get_serializer_context(self.reviewer_user, method="POST")
        data = {"business_user": self.business_user.id, "rating": 5, "description": "Duplicate!"}
        with patch("reviews_app.api.serializers.Review.objects.filter") as mock_filter:
            mock_filter.return_value.exists.return_value = True
            serializer = ReviewSerializer(data=data, context=context)
            with self.assertRaises(ValidationError) as cm:
                serializer.is_valid(raise_exception=True)
            self.assertIn(
                "You have already reviewed this business.", str(cm.exception.detail.get("non_field_errors", ""))
            )
            self.assertTrue(mock_filter.return_value.exists.called)

    def test_validate_user_is_none(self):
        context = self._get_serializer_context(self.reviewer_user, method="POST")
        drf_request = context["request"]
        drf_request.user = None
        data = {"business_user": self.other_business_user.id, "rating": 5, "description": "No user!"}
        serializer = ReviewSerializer(data=data, context={"request": drf_request})
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("user is not available", str(cm.exception.detail.get("non_field_errors", "")))
