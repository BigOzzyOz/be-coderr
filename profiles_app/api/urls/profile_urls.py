from django.urls import path
from profiles_app.api.views import ProfileDetailView

urlpatterns = [
    path("<int:pk>/", ProfileDetailView.as_view(), name="profile"),
]
