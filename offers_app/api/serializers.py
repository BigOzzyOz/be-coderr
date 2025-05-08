from rest_framework import serializers
from django.db import models
from django.contrib.auth.models import User
from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
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
    url = serializers.HyperlinkedIdentityField(view_name="offerdetails-detail", lookup_field="id", read_only=True)

    class Meta:
        model = OfferDetail
        fields = ("id", "url")
        read_only_fields = ["id"]


class OfferUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]
        read_only_fields = ["first_name", "last_name", "username"]


class OfferSerializer(serializers.ModelSerializer):
    user_details = OfferUserDetailSerializer(source="user", read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    details = OfferDetailSerializer(many=True, required=False)
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

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
        request = self.context.get("request")
        if request and request.method == "PATCH":
            raw_data = request.data
            if "details" in raw_data and isinstance(raw_data["details"], list) and not raw_data["details"]:
                raise serializers.ValidationError(
                    {"details": "At least one detail is required when providing the 'details' field for update."}
                )

        return attrs

    def get_min_price(self, obj):
        if obj.details.exists():
            return obj.details.aggregate(models.Min("price"))["price__min"]
        return None

    def get_min_delivery_time(self, obj):
        if obj.details.exists():
            return obj.details.aggregate(models.Min("delivery_time_in_days"))["delivery_time_in_days__min"]
        return None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method in ["GET"]:
            self.fields["details"] = OfferDetailLinkSerializer(many=True, read_only=True)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        details_data = validated_data.pop("details", [])
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            existing_details_mapping = {item.get("id"): item for item in details_data if item.get("id")}
            new_details_data = [item for item in details_data if not item.get("id")]

            for detail_id, data in existing_details_mapping.items():
                try:
                    detail_instance = OfferDetail.objects.get(id=detail_id, offer=instance)
                    data.pop("id", None)
                    for attr, value in data.items():
                        setattr(detail_instance, attr, value)
                    detail_instance.save()
                except OfferDetail.DoesNotExist:
                    pass

            for data in new_details_data:
                try:
                    OfferDetail.objects.create(offer=instance, **data)
                except Exception as e:
                    raise serializers.ValidationError(f"Failed to create a detail: {e}")

        return instance
