from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from profiles_app.models import Profile
from profiles_app.api.serializers import ProfileSerializer, CustomerProfileSerializer, BusinessProfileSerializer
from profiles_app.api.permissions import IsOwnerStaffOrReadOnly


class ProfileDetailView(RetrieveUpdateAPIView):
    """Retrieve and update a user profile by user PK."""

    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = [IsOwnerStaffOrReadOnly]
    lookup_field = "pk"

    def get_object(self):
        """Get the profile object for the given user PK."""
        user_pk = self.kwargs.get("pk")
        obj = Profile.objects.select_related("user").get(user__pk=user_pk)

        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        """Block PUT, allow PATCH for updates."""
        if request.method == "PUT":
            return Response(
                {"detail": "PUT is not allowed. Use PATCH instead."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        else:
            return super().update(request, *args, **kwargs)


class CustomerProfileListView(ListAPIView):
    """List all customer profiles."""

    serializer_class = CustomerProfileSerializer
    queryset = Profile.objects.filter(type="customer")
    pagination_class = None


class BusinessProfileListView(ListAPIView):
    """List all business profiles."""

    serializer_class = BusinessProfileSerializer
    queryset = Profile.objects.filter(type="business")
    pagination_class = None
