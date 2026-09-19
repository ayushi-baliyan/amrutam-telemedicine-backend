from django.urls import path

from .views import (
    PrescriptionCreateView,
    PrescriptionDetailView,
)

urlpatterns = [
    path(
        "",
        PrescriptionCreateView.as_view(),
        name="prescription-create",
    ),
    path(
        "<int:pk>/",
        PrescriptionDetailView.as_view(),
        name="prescription-detail",
    ),
]