from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedOrCustomerCreateOrBusinessUpdateOrStaffDelete(BasePermission):
    """Custom permission: Authenticated, customer can create, business can update, staff can delete."""

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
        """Check object-level permissions for the request."""
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method in ["PUT", "PATCH"] and obj.business_user == request.user:
            return True
        if request.method == "DELETE" and request.user.is_staff:
            return True
        return False
