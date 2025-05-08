from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from django.db import transaction


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
        attrs["username"] = attrs["username"].strip()
        attrs["email"] = attrs["email"].strip()

        GUEST_LOGINS = ["andrey", "kevin"]
        if attrs["username"] in GUEST_LOGINS and not User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError({"username": "Username already exists."})

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
        username = attrs.get("username").strip()
        password = attrs.get("password")

        GUEST_LOGINS = {
            "andrey": ("asdasd", "customer"),
            "kevin": ("asdasd24", "business"),
        }

        if username in GUEST_LOGINS:
            guest_password, guest_type = GUEST_LOGINS[username]
            if password == guest_password:
                with transaction.atomic():
                    user, created = User.objects.get_or_create(
                        username=username, defaults={"email": f"{username}@guest.local"}
                    )

                    if created or not user.check_password(password):
                        user.set_password(password)
                        user.save()
                        profile = user.profile
                        profile.type = guest_type
                        profile.save()
                attrs["user"] = user
                return attrs
            else:
                raise serializers.ValidationError({"non_field_errors": "Invalid username or password."})

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError({"non_field_errors": "Invalid username or password."})

        attrs["user"] = user
        return attrs
