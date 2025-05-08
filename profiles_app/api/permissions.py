from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerStaffOrReadOnly(BasePermission):
    """Custom permission: Only owner or staff can edit, others read-only."""

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions for profile access."""
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS or request.user.is_staff:
            return True
        elif obj.user == request.user:
            return True
        else:
            return False
