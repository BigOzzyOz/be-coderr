from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedOrCustomerCreateOrOwnerUpdateDelete(BasePermission):
    """Custom permission: Authenticated, customer can create, owner can update/delete."""

    def has_permission(self, request, view):
        """Check general permissions for the request."""
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == "POST" and request.user.profile.type == "customer":
            return True
        if request.method in ["PATCH", "DELETE", "PUT"]:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions for review access."""
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method in ["PUT", "PATCH", "DELETE"] and obj.reviewer == request.user:
            return True
        return False
