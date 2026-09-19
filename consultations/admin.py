from django.contrib import admin

from .models import Consultation


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "doctor",
        "slot",
        "status",
        "idempotency_key",
        "created_at",
    )

    list_filter = ("status", "doctor")

    search_fields = (
        "patient__username",
        "doctor__user__username",
        "idempotency_key",
    )