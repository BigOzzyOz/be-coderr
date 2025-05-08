from django.test import TestCase
from unittest.mock import patch
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    MethodNotAllowed,
    NotFound,
)
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from core.utils.exception_handler import custom_exception_handler


class TestCustomExceptionHandler(TestCase):
    """Tests for the custom DRF exception handler."""

    @patch("core.utils.exception_handler.exception_handler", return_value=None)
    def test_permission_denied(self, mock_default_handler):
        """Should return 403 for PermissionDenied exception."""
        exception = PermissionDenied("Access denied.")
        context = {}
        response = custom_exception_handler(exception, context)

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {"detail": "Access denied."})
        mock_default_handler.assert_called_once_with(exception, context)

    @patch("core.utils.exception_handler.exception_handler", return_value=None)
    def test_validation_error(self, mock_default_handler):
        """Should return 400 for ValidationError exception."""
        exception = ValidationError({"field": ["This field is required."]})
        context = {}
        response = custom_exception_handler(exception, context)

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"field": ["This field is required."]})
        mock_default_handler.assert_called_once_with(exception, context)

    @patch("core.utils.exception_handler.exception_handler", return_value=None)
    def test_authentication_failed(self, mock_default_handler):
        """Should return 401 for AuthenticationFailed exception."""
        exception = AuthenticationFailed("Invalid credentials.")
        context = {}
        response = custom_exception_handler(exception, context)

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, {"detail": "Invalid credentials."})
        mock_default_handler.assert_called_once_with(exception, context)

    @patch("core.utils.exception_handler.exception_handler", return_value=None)
    def test_not_authenticated(self, mock_default_handler):
        """Should return 401 for NotAuthenticated exception."""
        exception = NotAuthenticated("Authentication required.")
        context = {}
        response = custom_exception_handler(exception, context)

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, {"detail": "Authentication required."})
        mock_default_handler.assert_called_once_with(exception, context)

    @patch("core.utils.exception_handler.exception_handler", return_value=None)
    def test_method_not_allowed(self, mock_default_handler):
        """Should return 405 for MethodNotAllowed exception."""
        exception = MethodNotAllowed("GET", detail="Method 'GET' not allowed.")
        context = {}
        response = custom_exception_handler(exception, context)

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 405)
        self.assertIn("Method 'GET' not allowed.", response.data.get("detail", ""))
        mock_default_handler.assert_called_once_with(exception, context)

    def test_generic_exception(self):
        """Should return 500 for generic Exception."""
        exception = Exception("An unexpected error occurred.")
        context = {}
        with patch("core.utils.exception_handler.exception_handler", return_value=None) as mock_default_handler:
            response = custom_exception_handler(exception, context)
            mock_default_handler.assert_called_once_with(exception, context)

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data, {"detail": "Internal server error."})

    def test_not_found(self):
        """Should return 404 for NotFound exception."""
        exception = NotFound("Not found.")
        context = {}
        with patch("core.utils.exception_handler.exception_handler", return_value=None) as mock_default_handler:
            response = custom_exception_handler(exception, context)
            mock_default_handler.assert_called_once_with(exception, context)

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"detail": "Not found."})

    def test_http404(self):
        """Should return 404 for Django Http404 exception."""
        exception = Http404("Django not found.")
        context = {}
        with patch("core.utils.exception_handler.exception_handler", return_value=None) as mock_default_handler:
            response = custom_exception_handler(exception, context)
            mock_default_handler.assert_called_once_with(exception, context)

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"detail": "Django not found."})

    def test_object_does_not_exist(self):
        """Should return 404 for ObjectDoesNotExist exception."""
        exception = ObjectDoesNotExist("Object not found.")
        context = {}
        with patch("core.utils.exception_handler.exception_handler", return_value=None) as mock_default_handler:
            response = custom_exception_handler(exception, context)
            mock_default_handler.assert_called_once_with(exception, context)

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"detail": "Object not found."})
