from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    """Model for a review of a business by a user."""

    id = models.AutoField(primary_key=True, editable=False)
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="business_reviews")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reviews")
    rating = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("reviewer", "business_user")

    def __str__(self):
        """String representation of Review."""
        return f"Review by {self.reviewer.username} for {self.business_user.username}"
