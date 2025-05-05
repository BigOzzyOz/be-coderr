from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from profiles_app.models import Profile
from profiles_app.api.serializers import ProfileSerializer, CustomerProfileSerializer, BusinessProfileSerializer
from profiles_app.api.permissions import IsOwnerStaffOrReadOnly


class ProfileDetailView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = [IsOwnerStaffOrReadOnly]
    lookup_field = "pk"

    def get_object(self):
        user_pk = self.kwargs.get("pk")
        try:
            obj = Profile.objects.select_related("user").get(user__pk=user_pk)
        except Profile.DoesNotExist:
            raise NotFound("Profile not found.")

        self.check_object_permissions(self.request, obj)
        return obj

    def put(self, request, *args, **kwargs):
        return Response({"detail": "PUT is not allowed. Use PATCH instead."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CustomerProfileListView(ListAPIView):
    serializer_class = CustomerProfileSerializer
    queryset = Profile.objects.filter(type="customer")
    pagination_class = None


class BusinessProfileListView(ListAPIView):
    serializer_class = BusinessProfileSerializer
    queryset = Profile.objects.filter(type="business")
    pagination_class = None
