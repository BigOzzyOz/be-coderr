from django.utils import timezone
from rest_framework import serializers
from profiles_app.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.pk")
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

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
        if "file" in validated_data and not validated_data["file"] == instance.file:
            file = validated_data.pop("file")
            instance.file = file
            instance.uploaded_at = timezone.now()
        return super().update(instance, validated_data)


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.pk")
    uploaded_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

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
