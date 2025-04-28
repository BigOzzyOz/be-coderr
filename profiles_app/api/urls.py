from django.urls import path
from profiles_app.api.views import BusinessProfileListView, CustomerProfileListView, ProfileDetailView

urlpatterns = [
    path("profile/<int:pk>/", ProfileDetailView.as_view(), name="profile"),
    path("profiles/customer/", CustomerProfileListView.as_view(), name="customer_profiles"),
    path("profiles/business/", BusinessProfileListView.as_view(), name="business_profiles"),
]
