from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Email already exists.")]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Username already exists.")]
    )
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=["customer", "business"])

    class Meta:
        model = User
        fields = ("username", "email", "password", "repeated_password", "type")

    def validate(self, attrs):
        attrs["username"] = attrs["username"].lower().strip()
        attrs["email"] = attrs["email"].lower().strip()

        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError({"non_field_errors": "Passwords do not match."})

        return attrs

    def create(self, validated_data):
        validated_data.pop("repeated_password")
        validated_data.pop("type")
        validated_data["username"] = validated_data["username"]
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password")

    def validate(self, attrs):
        username = attrs.get("username").lower()
        password = attrs.get("password")

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError({"non_field_errors": "Invalid username or password."})

        attrs["user"] = user
        return attrs
