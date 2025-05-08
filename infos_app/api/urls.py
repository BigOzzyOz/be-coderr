from django.urls import path
from infos_app.api.views import BaseInfoView

app_name = "infos_app"

urlpatterns = [
    path("base-info/", BaseInfoView.as_view(), name="base-info"),
]
