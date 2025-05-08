from rest_framework import serializers
from django.db import models
from django.contrib.auth.models import User
from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializer for OfferDetail model."""

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        extra_kwargs = {"id": {"read_only": False, "required": False}}


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Serializer for OfferDetail with hyperlink."""

    url = serializers.HyperlinkedIdentityField(view_name="offerdetails-detail", lookup_field="id", read_only=True)

    class Meta:
        model = OfferDetail
        fields = ("id", "url")
        read_only_fields = ["id"]


class OfferUserDetailSerializer(serializers.ModelSerializer):
    """Serializer for user details in Offer."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]
        read_only_fields = ["first_name", "last_name", "username"]


class OfferSerializer(serializers.ModelSerializer):
    """Serializer for Offer model with details and user info."""

    user_details = OfferUserDetailSerializer(source="user", read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    details = OfferDetailSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = (
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        )
        read_only_fields = ["user", "id", "created_at", "updated_at"]

    def validate(self, attrs):
        """Validate offer details for creation and update."""

        request = self.context.get("request")
        details = attrs.get("details") or self.initial_data.get("details")
        if request and request.method == "POST":
            if not details or len(details) != 3:
                raise serializers.ValidationError(
                    {"details": "Exactly 3 details (basic, standard, premium) are required."}
                )
            types = [d.get("offer_type") for d in details]
            if set(types) != {"basic", "standard", "premium"}:
                raise serializers.ValidationError(
                    {"details": "You must provide one detail for each type: basic, standard, premium."}
                )
        if request and request.method == "PATCH":
            raw_data = request.data
            if "details" in raw_data and isinstance(raw_data["details"], list) and not raw_data["details"]:
                raise serializers.ValidationError(
                    {"details": "At least one detail is required when providing the 'details' field for update."}
                )

        return attrs

    def get_min_price(self, obj):
        """Get minimum price from offer details."""

        if obj.details.exists():
            return obj.details.aggregate(models.Min("price"))["price__min"]
        return None

    def get_min_delivery_time(self, obj):
        """Get minimum delivery time from offer details."""

        if obj.details.exists():
            return obj.details.aggregate(models.Min("delivery_time_in_days"))["delivery_time_in_days__min"]
        return None

    def __init__(self, *args, **kwargs):
        """Customize fields based on request method."""

        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method in ["GET"]:
            self.fields["details"] = OfferDetailLinkSerializer(many=True, read_only=True)

    def create(self, validated_data):
        """Create offer with details."""

        validated_data["user"] = self.context["request"].user
        details_data = validated_data.pop("details", [])
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        """Update offer and its details."""

        details_data = validated_data.pop("details", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if details_data is not None:
            for new_detail in details_data:
                offer_type = new_detail.get("offer_type")
                old_detail = instance.details.filter(offer_type=offer_type).first()
                if old_detail:
                    for key, value in new_detail.items():
                        setattr(old_detail, key, value)
                    old_detail.save()
                else:
                    raise serializers.ValidationError(
                        {
                            "details": f"No existing detail with offer_type '{offer_type}' found. Cannot create new details on update."
                        }
                    )
        return instance
