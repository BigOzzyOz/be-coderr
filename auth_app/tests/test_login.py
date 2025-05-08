from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from profiles_app.models import Profile
from core.utils.test_client import JSONAPIClient


class TestLogin(APITestCase):
    """Test cases for user login API."""

    client_class = JSONAPIClient

    def test_login_success(self):
        """Test successful login with valid credentials."""
        user = User.objects.create_user(username="loginuser", email="login@mail.de", password="pw123")
        Profile.objects.filter(user=user).update(type="customer")
        data = {"username": "loginuser", "password": "pw123"}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "loginuser")
        self.assertEqual(response.data["email"], "login@mail.de")

    def test_login_wrong_password(self):
        """Test login with wrong password returns error."""
        User.objects.create_user(username="user7", email="user7@mail.de", password="pw123")
        data = {"username": "user7", "password": "wrongpw"}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)

    def test_login_nonexistent_user(self):
        """Test login with non-existent user returns error."""
        data = {"username": "nouser", "password": "pw123"}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)

    def test_login_missing_fields(self):
        """Test login with missing fields returns error."""
        data = {}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)
        self.assertIn("password", response.data)

    def test_login_internal_server_error(self):
        """Test login returns 500 on internal server error."""
        self.client.raise_request_exception = False
        from django.contrib.auth.models import User

        original_get = User.objects.get

        def error_get(*args, **kwargs):
            raise Exception("Test-Fehler")

        User.objects.get = error_get
        data = {"username": "somebody", "password": "somewhat"}
        try:
            response = self.client.post(reverse("login"), data)
            self.assertEqual(response.status_code, 500)
            self.assertIn("server error", response.data["detail"])
        finally:
            User.objects.get = original_get

    def test_login_guest_customer(self):
        """Test guest customer login returns correct profile type."""
        data = {"username": "andrey", "password": "asdasd"}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "andrey")
        self.assertEqual(response.data["email"], "andrey@guest.local")

        from profiles_app.models import Profile

        profile = Profile.objects.get(user__username="andrey")
        self.assertEqual(profile.type, "customer")

    def test_login_guest_business(self):
        """Test guest business login returns correct profile type."""
        data = {"username": "kevin", "password": "asdasd24"}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "kevin")
        self.assertEqual(response.data["email"], "kevin@guest.local")
        from profiles_app.models import Profile

        profile = Profile.objects.get(user__username="kevin")
        self.assertEqual(profile.type, "business")

    def test_login_guest_wrong_password(self):
        """Test guest login with wrong password returns error."""
        data = {"username": "andrey", "password": "falsch"}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)
        self.assertIn("invalid", str(response.data["non_field_errors"]).lower())
