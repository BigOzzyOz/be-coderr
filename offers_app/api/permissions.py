from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedOrBusinessCreateOrOwnerUpdateDelete(BasePermission):
    """Custom permission: Authenticated, business can create, owner can update/delete."""

    def has_permission(self, request, view):
        """Check general permissions for the request."""
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == "POST" and request.user.profile.type == "business":
            return True
        if request.method in ["PATCH", "DELETE", "PUT"]:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions for the request."""
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method in ["PUT", "PATCH", "DELETE"] and obj.user == request.user:
            return True
        return False
