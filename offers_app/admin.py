from django.contrib import admin
from offers_app.models import Offer, OfferDetail

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "created_at", "updated_at")
    search_fields = ("title", "description", "user__username")
    list_filter = ("created_at", "updated_at", "user")
    ordering = ("-created_at",)
    list_per_page = 20
    list_display_links = ("id", "title")

@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = ("id", "offer", "title", "price", "delivery_time_in_days", "offer_type")
    search_fields = ("title", "offer__title")
    list_filter = ("offer_type", "delivery_time_in_days")
    ordering = ("offer", "id")
    list_per_page = 20
    list_display_links = ("id", "title")
