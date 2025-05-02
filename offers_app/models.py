from django.db import models
from django.contrib.auth.models import User


class OfferDetailModel(models.Model):
    OFFER_TYPE_CHOICES = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    revisions = models.CharField(max_length=255, blank=True, null=True)
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list, blank=True, null=True)
    offer_type = models.CharField(choices=OFFER_TYPE_CHOICES, max_length=50, blank=True)
    offer = models.ForeignKey("OfferModel", on_delete=models.CASCADE, related_name="offer_detail", default=None)

    def __str__(self):
        return self.title


class OfferModel(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to="offers/", blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Offer by {self.user.username} for {self.offer_detail.title}"
