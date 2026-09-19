from django.contrib import admin

from .models import Doctor, AvailabilitySlot


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "specialization",
        "experience_years",
        "consultation_fee",
        "is_verified",
        "is_available",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "specialization",
        "registration_number",
    )


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "doctor",
        "start_time",
        "end_time",
        "status",
    )

    list_filter = ("status", "doctor")