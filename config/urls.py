from django.contrib import admin
from django.urls import path, include
from .views import health_check
from django_prometheus import exports

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path("admin/", admin.site.urls),

    # API
    path(
        "api/users/",
        include("users.urls"),
    ),

    path(
        "api/doctors/",
        include("doctors.urls"),
    ),

    path(
        "api/consultations/",
        include("consultations.urls"),
    ),

    path(
        "api/prescriptions/",
        include("prescriptions.urls"),
    ),
    path("api/payments/", include("payments.urls")),

    # OpenAPI
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),

    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
        name="swagger-ui",
    ),
    path(
    "health/",
    health_check,
    name="health-check",
),
path("metrics/", exports.ExportToDjangoView, name="prometheus-metrics"),
]