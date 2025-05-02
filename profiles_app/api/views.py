from rest_framework.exceptions import NotFound, AuthenticationFailed, PermissionDenied, NotAuthenticated
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
            obj = Profile.objects.get(user__pk=user_pk)
        except Profile.DoesNotExist:
            raise NotFound("Profile not found.")

        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        try:
            profile = self.get_object()
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            if isinstance(e, (AuthenticationFailed, NotAuthenticated)):
                return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            elif isinstance(e, NotFound):
                return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, *args, **kwargs):
        return Response({"detail": "PUT is not allowed. Use PATCH instead."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        try:
            profile = self.get_object()
            serializer = ProfileSerializer(profile, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            if isinstance(e, (AuthenticationFailed, NotAuthenticated)):
                return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            elif isinstance(e, NotFound):
                return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
            elif isinstance(e, PermissionDenied):
                return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerProfileListView(ListAPIView):
    serializer_class = CustomerProfileSerializer
    queryset = Profile.objects.filter(type="customer")

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BusinessProfileListView(ListAPIView):
    serializer_class = BusinessProfileSerializer
    queryset = Profile.objects.filter(type="business")

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
