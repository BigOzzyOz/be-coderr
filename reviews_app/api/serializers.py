from rest_framework import serializers
from reviews_app.models import Review
from django.contrib.auth.models import User


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_business_user(self, value):
        try:
            if not hasattr(value, "profile") or value.profile.type != "business":
                raise serializers.ValidationError("The selected user does not have a business profile.")
        except AttributeError:
            raise serializers.ValidationError("The selected user does not have an associated profile.")

        if self.context["request"].user == value:
            raise serializers.ValidationError("You cannot review yourself.")
        return value

    def update(self, instance, validated_data):
        validated_data.pop("business_user", None)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        actual_user = self.context["request"].user
        validated_data["reviewer"] = actual_user
        instance = Review.objects.create(**validated_data)
        return instance
