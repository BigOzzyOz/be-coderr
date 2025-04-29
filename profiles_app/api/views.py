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
    lookup_field = "user__pk"

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        return Response({"detail": "PUT is not allowed. Use PATCH instead."}, status=405)

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerProfileListView(ListAPIView):
    serializer_class = CustomerProfileSerializer
    queryset = Profile.objects.filter(type="customer")

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BusinessProfileListView(ListAPIView):
    serializer_class = BusinessProfileSerializer
    queryset = Profile.objects.filter(type="business")

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
