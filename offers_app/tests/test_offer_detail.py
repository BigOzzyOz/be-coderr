from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from core.utils.test_client import JSONAPIClient
from offers_app.models import Offer, OfferDetail
from offers_app.api.views import OfferModelViewSet


class TestOfferDetailView(APITestCase):
    client_class = JSONAPIClient

    @classmethod
    def setUpTestData(cls):
        cls.business_user = User.objects.create_user(username="business", password="pw123", email="b@mail.de")
        cls.business_user.profile.type = "business"
        cls.business_user.profile.save()
        cls.other_user = User.objects.create_user(username="other", password="pw123", email="o@mail.de")
        cls.other_user.profile.type = "business"
        cls.other_user.profile.save()
        cls.offer = Offer.objects.create(user=cls.business_user, title="Test", description="desc")
        OfferDetail.objects.create(
            offer=cls.offer,
            title="Detail1",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["A"],
            offer_type="basic",
        )
        cls.url = reverse("offer-detail", kwargs={"pk": cls.offer.pk})

    def setUp(self):
        self.client = self.client_class()

    def test_get_offer_detail_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_get_offer_detail_authenticated(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.offer.pk)

    def test_get_offer_detail_not_found(self):
        self.client.force_authenticate(user=self.business_user)
        url = reverse("offer-detail", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_offer_detail_internal_server_error(self):
        self.client.force_authenticate(user=self.business_user)
        orig_get_queryset = OfferModelViewSet.get_queryset

        def error_get_queryset(self):
            raise Exception("Test-Fehler")

        OfferModelViewSet.get_queryset = error_get_queryset
        try:
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 500)
            self.assertIn("detail", response.data)
        finally:
            OfferModelViewSet.get_queryset = orig_get_queryset

    def test_put_offer_not_allowed(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.put(self.url, {"title": "PUT"})
        self.assertEqual(response.status_code, 405)

    def test_patch_offer_unauthenticated(self):
        response = self.client.patch(self.url, {"title": "Patch"})
        self.assertEqual(response.status_code, 401)

    def test_patch_offer_not_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(self.url, {"title": "Patch"})
        self.assertEqual(response.status_code, 403)

    def test_patch_offer_not_found(self):
        self.client.force_authenticate(user=self.business_user)
        url = reverse("offer-detail", kwargs={"pk": 9999})
        response = self.client.patch(url, {"title": "Patch"})
        self.assertEqual(response.status_code, 404)

    def test_patch_offer_invalid_data(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.patch(self.url, {"details": []})
        self.assertEqual(response.status_code, 400)

    def test_patch_offer_success(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.patch(self.url, {"title": "Patched"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Patched")

    def test_patch_offer_internal_server_error(self):
        self.client.force_authenticate(user=self.business_user)
        orig_save = Offer.save
        Offer.save = lambda *a, **kw: (_ for _ in ()).throw(Exception("Test-Fehler"))
        try:
            response = self.client.patch(self.url, {"title": "Patch"})
            self.assertEqual(response.status_code, 500)
        finally:
            Offer.save = orig_save

    def test_delete_offer_unauthenticated(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 401)

    def test_delete_offer_not_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)

    def test_delete_offer_not_found(self):
        self.client.force_authenticate(user=self.business_user)
        url = reverse("offer-detail", kwargs={"pk": 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_delete_offer_success(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)

    def test_delete_offer_internal_server_error(self):
        self.client.force_authenticate(user=self.business_user)
        orig_delete = Offer.delete
        Offer.delete = lambda *a, **kw: (_ for _ in ()).throw(Exception("Test-Fehler"))
        try:
            response = self.client.delete(self.url)
            self.assertEqual(response.status_code, 500)
        finally:
            Offer.delete = orig_delete
