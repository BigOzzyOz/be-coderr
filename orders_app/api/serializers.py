from rest_framework import serializers
from orders_app.models import Order
from offers_app.models import OfferDetail


class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
            "offer_detail_id",
        ]
        read_only_fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "customer_user": {"required": False},
            "business_user": {"required": False},
            "title": {"required": False},
            "revisions": {"required": False},
            "delivery_time_in_days": {"required": False},
            "price": {"required": False},
            "features": {"required": False},
            "offer_type": {"required": False},
            "status": {"required": False},
        }

    def create(self, validated_data):
        offer_detail_id = validated_data.pop("offer_detail_id")
        offer = OfferDetail.objects.get(id=offer_detail_id)
        validated_data["title"] = offer.title
        validated_data["revisions"] = offer.revisions
        validated_data["delivery_time_in_days"] = offer.delivery_time_in_days
        validated_data["price"] = offer.price
        validated_data["features"] = offer.features
        validated_data["offer_type"] = offer.offer_type
        validated_data["customer_user"] = self.context["request"].user
        validated_data["business_user"] = offer.offer.user
        validated_data["status"] = "in_progress"
        order = Order.objects.create(**validated_data)
        order.save()
        return order
