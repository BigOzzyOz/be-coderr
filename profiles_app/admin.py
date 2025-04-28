from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "username",
        "first_name",
        "last_name",
        "file",
        "location",
        "tel",
        "description",
        "working_hours",
        "type",
        "email",
        "created_at",
    )
    search_fields = ("username", "email")
    list_filter = ("type", "created_at")
    ordering = ("-created_at",)
    list_per_page = 20
    list_display_links = ("user", "username")
    fieldsets = (
        (None, {"fields": ("user", "username", "email")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "file", "location", "tel", "description")}),
        ("Business Info", {"fields": ("working_hours", "type")}),
        ("Date Information", {"fields": ("created_at",)}),
    )
