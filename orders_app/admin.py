from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model."""

    list_display = ("id", "title", "customer_user", "business_user", "price", "status", "created_at", "updated_at")
    list_filter = ("status", "offer_type", "created_at", "business_user")
    search_fields = ("title", "customer_user__username", "business_user__username")
    autocomplete_fields = ["customer_user", "business_user"]
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": ("title", "customer_user", "business_user", "offer_type", "status", "price")}),
        ("Details", {"fields": ("revisions", "delivery_time_in_days", "features")}),
        ("Zeitstempel", {"fields": ("created_at", "updated_at")}),
    )
