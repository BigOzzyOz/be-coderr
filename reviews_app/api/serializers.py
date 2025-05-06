from rest_framework import serializers
from reviews_app.models import Review
from django.contrib.auth.models import User
from django.db import IntegrityError


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    business_user_username = serializers.CharField(source="business_user.username", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "reviewer",
            "business_user",
            "business_user_username",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reviewer", "created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError("Request context is missing or user is not available.")

        reviewer = request.user
        business_user = attrs.get("business_user")

        if business_user and business_user == reviewer:
            raise serializers.ValidationError("Users cannot review themselves.")

        if self.instance is None and business_user:
            if Review.objects.filter(reviewer=reviewer, business_user=business_user).exists():
                raise serializers.ValidationError({"non_field_errors": ["You have already reviewed this business."]})

        return attrs

    def create(self, validated_data):
        validated_data["reviewer"] = self.context["request"].user
        try:
            instance = Review.objects.create(**validated_data)
            return instance
        except IntegrityError:
            raise serializers.ValidationError({"non_field_errors": ["This review already exists."]})

    def update(self, instance, validated_data):
        validated_data.pop("business_user", None)
        validated_data.pop("reviewer", None)
        return super().update(instance, validated_data)
