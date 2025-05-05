from django.contrib import admin
from .models import Review
# Register your models here.


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin-Interface-Konfiguration für das Review-Modell.
    """

    list_display = ("id", "reviewer_username", "business_username", "rating", "created_at", "updated_at")
    list_filter = ("rating", "created_at", "updated_at")
    search_fields = ("reviewer__username", "business_user__username", "description")
    list_display_links = ("id", "reviewer_username", "business_username")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("business_user", "reviewer", "rating")}),
        ("Details", {"fields": ("description",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def reviewer_username(self, obj):
        return obj.reviewer.username

    reviewer_username.short_description = "Reviewer"

    def business_username(self, obj):
        return obj.business_user.username

    business_username.short_description = "Business User"
