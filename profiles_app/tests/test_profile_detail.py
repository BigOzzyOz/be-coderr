import os
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from core.utils.test_client import JSONAPIClient
from profiles_app.models import Profile
from profiles_app.api.views import ProfileDetailView


class TestProfileDetailView(APITestCase):
    client_class = JSONAPIClient

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pw123", email="test@mail.de")
        self.profile = self.user.profile
        self.profile.type = "customer"
        self.profile.save()
        self.url = reverse("profile", kwargs={"pk": self.user.pk})

    def test_get_profile_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)

    def test_get_profile_not_found(self):
        self.client.force_authenticate(user=self.user)
        self.profile.delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.data)

    def test_get_profile_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"], self.user.pk)
        self.assertEqual(response.data["username"], self.user.username)

    def test_get_profile_internal_server_error(self):
        self.client.force_authenticate(user=self.user)
        orig_get_object = ProfileDetailView.get_object

        def error_get_object(self):
            raise Exception("Test-Error")

        ProfileDetailView.get_object = error_get_object
        try:
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 500)
            self.assertIn("detail", response.data)
        finally:
            ProfileDetailView.get_object = orig_get_object

    def test_patch_profile_success(self):
        self.client.force_authenticate(user=self.user)
        data = {"first_name": "Max", "last_name": "Mustermann"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "Max")
        self.assertEqual(response.data["last_name"], "Mustermann")

    def test_patch_profile_unauthenticated(self):
        data = {"first_name": "Max"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)

    def test_patch_profile_not_owner(self):
        other = User.objects.create_user(username="other", password="pw123", email="other@mail.de")
        self.client.force_authenticate(user=other)
        data = {"first_name": "Hacker"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 403)
        self.assertIn("detail", response.data)

    def test_patch_profile_not_found(self):
        self.client.force_authenticate(user=self.user)
        self.profile.delete()
        data = {"first_name": "Ghost"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.data)

    def test_patch_profile_internal_server_error(self):
        self.client.force_authenticate(user=self.user)
        orig_save = Profile.save
        Profile.save = lambda *a, **kw: (_ for _ in ()).throw(Exception("Test-Fehler"))
        data = {"first_name": "Fehler"}
        try:
            response = self.client.patch(self.url, data)
            self.assertEqual(response.status_code, 500)
            self.assertIn("detail", response.data)
        finally:
            Profile.save = orig_save

    def test_put_profile_not_allowed(self):
        self.client.force_authenticate(user=self.user)
        data = {"first_name": "PUT"}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, 405)
        self.assertIn("detail", response.data)

    def test_profile_str_method(self):
        self.client.force_authenticate(user=self.user)
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(str(profile), f"{self.user.username}'s Profile")

    def test_profile_IsOwnerOrStaff_permission_staff(self):
        staff_user = User.objects.create_user(username="staffuser", password="pw123", email="")
        staff_user.is_staff = True
        staff_user.save()
        self.client.force_authenticate(user=staff_user)
        data = {"first_name": "Hacker"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "Hacker")

    def test_profile_IsOwnerOrStaff_permission_not_owner(self):
        other_user = User.objects.create_user(username="otheruser", password="pw123", email="")
        self.client.force_authenticate(user=other_user)
        data = {"first_name": "Hacker"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 403)
        self.assertIn("detail", response.data)

    def test_patch_bad_request(self):
        self.client.force_authenticate(user=self.user)
        data = {"email": "not-an-email"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)
        self.assertTrue(any("valid email" in str(msg).lower() for msg in response.data["email"]))

    def test_patch_profile_file_sets_uploaded_at(self):
        self.client.force_authenticate(user=self.user)
        file = SimpleUploadedFile("test.txt", b"content")
        data = {"file": file}
        response = self.client.patch(self.url, data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertIsNotNone(self.profile.uploaded_at)
        if self.profile.file:
            try:
                os.remove(self.profile.file.path)
            except Exception:
                pass
