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
        read_only_fields = ["id"]


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
        read_only_fields = ["id", "created_at", "updated_at"]

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
        else:
            self.fields["details"] = OfferDetailSerializer(many=True)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        details_data = validated_data.pop("details", None)
        offer = Offer.objects.create(**validated_data)
        if details_data:
            for detail_data in details_data:
                OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.image = validated_data.get("image", instance.image)
        instance.save()

        if details_data:
            for detail_data in details_data:
                detail_id = detail_data.get("id")
                if detail_id:
                    detail_instance = OfferDetail.objects.get(id=detail_id, offer=instance)
                    for attr, value in detail_data.items():
                        setattr(detail_instance, attr, value)
                    detail_instance.save()
                else:
                    OfferDetail.objects.create(offer=instance, **detail_data)

        return instance
