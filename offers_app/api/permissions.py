from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedOrBusinessCreateOrOwnerUpdateDelete(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == "POST" and request.user.profile.type == "business":
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method in ["PATCH", "DELETE"] and obj.user == request.user:
            return True
        return False
