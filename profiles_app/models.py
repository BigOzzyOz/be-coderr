from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    """Model for user profile with business and customer types."""

    TYPE_CHOICES = [
        ("customer", "Customer"),
        ("business", "Business"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    file = models.FileField(upload_to="profiles/", blank=True, null=True)
    uploaded_at = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    tel = models.CharField(max_length=25, blank=True)
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=50, blank=True)
    type = models.CharField(choices=TYPE_CHOICES, max_length=50, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """String representation of Profile."""
        return f"{self.user.username}'s Profile"
