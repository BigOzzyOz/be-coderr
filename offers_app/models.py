from django.db import models
from django.contrib.auth.models import User


class OfferDetail(models.Model):
    """Model for offer details (basic, standard, premium)."""

    OFFER_TYPE_CHOICES = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    revisions = models.IntegerField(default=0)
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list, blank=True, null=True)
    offer_type = models.CharField(choices=OFFER_TYPE_CHOICES, max_length=50)
    offer = models.ForeignKey("Offer", on_delete=models.CASCADE, related_name="details", default=None)

    def __str__(self):
        """String representation of OfferDetail."""
        return self.title


class Offer(models.Model):
    """Model for an offer posted by a user."""

    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to="offers/", blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation of Offer."""
        return f"Offer by {self.user.username} for {self.title}"
