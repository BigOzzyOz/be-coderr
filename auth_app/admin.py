from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_active")
    ordering = ("-date_joined",)
    list_per_page = 20
    list_display_links = ("id", "username")
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"fields": ("username", "email", "password1", "password2")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
