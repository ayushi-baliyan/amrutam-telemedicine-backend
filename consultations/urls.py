from django.urls import path

from .views import (
    ConsultationListView,
    ConsultationCreateView,
    ConsultationDetailView,
    ConsultationStatusUpdateView,
)


urlpatterns = [
    path(
        "",
        ConsultationListView.as_view(),
        name="consultation-list",
    ),
    path(
        "book/",
        ConsultationCreateView.as_view(),
        name="consultation-book",
    ),
    path(
        "<int:pk>/",
        ConsultationDetailView.as_view(),
        name="consultation-detail",
    ),
    path(
        "<int:pk>/status/",
        ConsultationStatusUpdateView.as_view(),
        name="consultation-status",
    ),
]