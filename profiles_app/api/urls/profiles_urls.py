from django.urls import path
from profiles_app.api.views import BusinessProfileListView, CustomerProfileListView

urlpatterns = [
    path("customer/", CustomerProfileListView.as_view(), name="customer_profiles"),
    path("business/", BusinessProfileListView.as_view(), name="business_profiles"),
]
