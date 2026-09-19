from django.contrib import admin

from .models import Prescription


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "consultation",
        "created_at",
        "updated_at",
    ]

    search_fields = [
        "consultation__patient__username",
        "consultation__doctor__user__username",
    ]