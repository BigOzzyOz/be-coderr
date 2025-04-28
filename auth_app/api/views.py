from rest_framework.authtoken.models import Token
from django.db import transaction
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from profiles_app.models import Profile
from .serializers import RegisterSerializer


class RegisterView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    profile, created = Profile.objects.get_or_create(user=user)
                    profile.type = request.data.get("type", "customer")
                    profile.save()
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response(
                        {"token": token.key, "username": user.username, "email": user.email, "user_id": user.id},
                        status=status.HTTP_201_CREATED,
                    )
            except Exception as e:
                print(f"Error creating user: {e}")
                return Response({"detail": "Internal server error."}, status=500)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.validated_data["user"]
                token, _ = Token.objects.get_or_create(user=user)
                return Response(
                    {"token": token.key, "username": user.username, "email": user.email, "user_id": user.id},
                    status=status.HTTP_200_OK,
                )
            except Exception:
                return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
