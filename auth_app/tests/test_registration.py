from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.utils.test_client import JSONAPIClient


class TestRegistration(APITestCase):
    client_class = JSONAPIClient

    def test_registration_success(self):
        data = {
            "username": "TestUser ",
            "email": "Test@Mail.DE ",
            "password": "testpass123",
            "repeated_password": "testpass123",
            "type": "customer",
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@mail.de")
        user = User.objects.get(username="testuser")
        self.assertEqual(user.profile.type, "customer")

    def test_registration_duplicate_username(self):
        User.objects.create_user(username="dupe", email="dupe@mail.de", password="pw")
        data = {
            "username": "dupe",
            "email": "new@mail.de",
            "password": "pw123",
            "repeated_password": "pw123",
            "type": "customer",
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)

    def test_registration_duplicate_email(self):
        User.objects.create_user(username="user1", email="dupe@mail.de", password="pw")
        data = {
            "username": "user2",
            "email": "dupe@mail.de",
            "password": "pw123",
            "repeated_password": "pw123",
            "type": "customer",
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_registration_invalid_email(self):
        data = {
            "username": "user3",
            "email": "notanemail",
            "password": "pw123",
            "repeated_password": "pw123",
            "type": "customer",
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_registration_password_mismatch(self):
        data = {
            "username": "user4",
            "email": "user4@mail.de",
            "password": "pw123",
            "repeated_password": "pw124",
            "type": "customer",
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)

    def test_registration_invalid_type(self):
        data = {
            "username": "user5",
            "email": "user5@mail.de",
            "password": "pw123",
            "repeated_password": "pw123",
            "type": "invalidtype",
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("type", response.data)

    def test_registration_missing_fields(self):
        data = {"username": "user6"}
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)
        self.assertIn("repeated_password", response.data)
        self.assertIn("type", response.data)

    def test_registration_internal_server_error(self):
        data = {
            "username": "erroruser",
            "email": "error@mail.de",
            "password": "pw123456",
            "repeated_password": "pw123456",
            "type": "customer",
        }
        response = self.client.post(reverse("register"), data)
        from django.contrib.auth.models import User
        from profiles_app.models import Profile

        user = User.objects.get(username="erroruser")
        Profile.objects.filter(user=user).delete()

        data2 = {
            "username": "erroruser2",
            "email": "error2@mail.de",
            "password": "pw123456",
            "repeated_password": "pw123456",
            "type": "customer",
        }

        original_save = User.save

        def error_save(self, *a, **kw):
            raise Exception("Test-Fehler")

        User.save = error_save
        try:
            response = self.client.post(reverse("register"), data2)
            self.assertEqual(response.status_code, 500)
            self.assertIn("detail", response.data)
        finally:
            User.save = original_save
