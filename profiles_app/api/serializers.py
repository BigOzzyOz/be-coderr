from django.utils import timezone
from rest_framework import serializers
from profiles_app.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the Profile model."""

    user = serializers.ReadOnlyField(source="user.pk")

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        read_only_fields = ["user", "username", "type", "created_at"]

    def update(self, instance, validated_data):
        """Update profile and set uploaded_at if file changes."""
        if "file" in validated_data and not validated_data["file"] == instance.file:
            file = validated_data.pop("file")
            instance.file = file
            instance.uploaded_at = timezone.now()
        return super().update(instance, validated_data)


class CustomerProfileSerializer(serializers.ModelSerializer):
    """Serializer for customer profiles."""

    user = serializers.ReadOnlyField(source="user.pk")

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "uploaded_at",
            "type",
        ]


class BusinessProfileSerializer(serializers.ModelSerializer):
    """Serializer for business profiles."""

    user = serializers.ReadOnlyField(source="user.pk")

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]
