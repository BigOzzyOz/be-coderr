from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from profiles_app.models import Profile
from core.utils.test_client import JSONAPIClient


class TestLogin(APITestCase):
    client_class = JSONAPIClient

    def test_login_success(self):
        user = User.objects.create_user(username="loginuser", email="login@mail.de", password="pw123")
        Profile.objects.filter(user=user).update(type="customer")
        data = {"username": "LOGINUSER ", "password": "pw123"}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "loginuser")
        self.assertEqual(response.data["email"], "login@mail.de")

    def test_login_wrong_password(self):
        User.objects.create_user(username="user7", email="user7@mail.de", password="pw123")
        data = {"username": "user7", "password": "wrongpw"}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)

    def test_login_nonexistent_user(self):
        data = {"username": "nouser", "password": "pw123"}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)

    def test_login_missing_fields(self):
        data = {}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)
        self.assertIn("password", response.data)

    def test_login_internal_server_error(self):
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
