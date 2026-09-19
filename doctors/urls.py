from django.urls import path

from .views import (
    DoctorListView,
    DoctorDetailView,
    AvailabilitySlotListCreateView,
)


urlpatterns = [
    path(
        "",
        DoctorListView.as_view(),
        name="doctor-list",
    ),

    path(
        "<int:pk>/",
        DoctorDetailView.as_view(),
        name="doctor-detail",
    ),

    path(
        "availability/",
        AvailabilitySlotListCreateView.as_view(),
        name="availability-list-create",
    ),
]