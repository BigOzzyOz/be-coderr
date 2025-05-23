import os
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from core.utils.test_client import JSONAPIClient
from profiles_app.models import Profile
from profiles_app.api.views import ProfileDetailView


class TestProfileDetailView(APITestCase):
    """Tests for profile detail API endpoint (retrieve, update, permissions, file upload)."""
    client_class = JSONAPIClient

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="pw123", email="test@mail.de")
        cls.profile = cls.user.profile
        cls.profile.type = "customer"
        cls.profile.save()
        cls.url = reverse("profile", kwargs={"pk": cls.user.pk})

    def setUp(self):
        self.client = self.client_class()

    def test_get_profile_unauthenticated(self):
        """Test that unauthenticated users cannot retrieve a profile."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)

    def test_get_profile_not_found(self):
        """Test that retrieving a non-existent profile returns 404."""
        self.client.force_authenticate(user=self.user)
        self.profile.delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.data)

    def test_get_profile_success(self):
        """Test that authenticated user can retrieve their profile."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"], self.user.pk)
        self.assertEqual(response.data["username"], self.user.username)

    def test_get_profile_internal_server_error(self):
        """Test that internal server error returns 500 for profile detail."""
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
        """Test that authenticated user can update their profile."""
        self.client.force_authenticate(user=self.user)
        data = {"first_name": "Max", "last_name": "Mustermann"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "Max")
        self.assertEqual(response.data["last_name"], "Mustermann")

    def test_patch_profile_unauthenticated(self):
        """Test that unauthenticated users cannot update a profile."""
        data = {"first_name": "Max"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)

    def test_patch_profile_not_owner(self):
        """Test that non-owners cannot update another user's profile."""
        other = User.objects.create_user(username="other", password="pw123", email="other@mail.de")
        self.client.force_authenticate(user=other)
        data = {"first_name": "Hacker"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 403)
        self.assertIn("detail", response.data)

    def test_patch_profile_not_found(self):
        """Test that updating a non-existent profile returns 404."""
        self.client.force_authenticate(user=self.user)
        self.profile.delete()
        data = {"first_name": "Ghost"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.data)

    def test_patch_profile_internal_server_error(self):
        """Test that internal server error returns 500 for profile update."""
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
        """Test that PUT is not allowed on profile detail view."""
        self.client.force_authenticate(user=self.user)
        data = {"first_name": "PUT"}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, 405)
        self.assertIn("detail", response.data)

    def test_profile_str_method(self):
        """Test the __str__ method of the Profile model."""
        self.client.force_authenticate(user=self.user)
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(str(profile), f"{self.user.username}'s Profile")

    def test_profile_IsOwnerOrStaff_permission_staff(self):
        """Test that staff can update any profile."""
        staff_user = User.objects.create_user(username="staffuser", password="pw123", email="")
        staff_user.is_staff = True
        staff_user.save()
        self.client.force_authenticate(user=staff_user)
        data = {"first_name": "Hacker"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "Hacker")

    def test_profile_IsOwnerOrStaff_permission_not_owner(self):
        """Test that non-owners cannot update another user's profile."""
        other_user = User.objects.create_user(username="otheruser", password="pw123", email="")
        self.client.force_authenticate(user=other_user)
        data = {"first_name": "Hacker"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 403)
        self.assertIn("detail", response.data)

    def test_patch_bad_request(self):
        """Test that invalid patch data returns 400."""
        self.client.force_authenticate(user=self.user)
        data = {"email": "not-an-email"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)
        self.assertTrue(any("valid email" in str(msg).lower() for msg in response.data["email"]))

    def test_patch_profile_file_sets_uploaded_at(self):
        """Test that uploading a file sets uploaded_at timestamp."""
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

    def test_patch_profile_file_upload(self):
        """Test that file upload works and file content is correct."""
        self.client.force_authenticate(user=self.user)
        file = SimpleUploadedFile("avatar.jpg", b"dummyimagecontent", content_type="image/jpeg")
        data = {"file": file}
        response = self.client.patch(self.url, data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.file)
        self.assertTrue(self.profile.file.name.endswith("avatar.jpg"))
        file_path = self.profile.file.path
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "rb") as f:
            content = f.read()
            self.assertEqual(content, b"dummyimagecontent")
        if self.profile.file:
            try:
                os.remove(self.profile.file.path)
            except Exception:
                pass
